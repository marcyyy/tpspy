from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q, Count, FloatField, Max
from .models import Tenant, Complaint, Billing, Visitor
from information.forms import RegistrationForm, UserLoginForm, UserUpdateForm, TenantForm, ComplaintForm, VisitorForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView
from django.forms import modelformset_factory, inlineformset_factory
from django.db.models.functions import Cast, StrIndex, Substr


def profile(request):
    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending')\
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    args = {'user':request.user, 'info_tenant_id': request.user.tenant.id, 'notif':notif,
            'bill_include':bill_include, 'visit_include':visit_include,}
    return render(request,'information/profile.html',args)


def analytics(request):
    tctr = Tenant.objects.count()
    cctr = Complaint.objects.count()
    bctr = Billing.objects.count()
    vctr = Visitor.objects.count()
    uctr2 = User.objects.count()

    cmctr = Complaint.objects.filter(complain='Maintenance').count()
    csctr = Complaint.objects.filter(complain='Staff').count()
    cnctr = Complaint.objects.filter(complain='Neighbour').count()
    cpctr = Complaint.objects.filter(complain='Pest').count()
    cpcctr = Complaint.objects.filter(complain='Property_Condition').count()
    cscctr = Complaint.objects.filter(complain='Safety').count()
    cbctr = Complaint.objects.filter(complain='Billing').count()
    coctr = Complaint.objects.filter(complain='Others').count()

    cavg = cmctr + cscctr + csctr + cnctr + cpctr + cpcctr + cbctr + coctr
    cfloat = Complaint.objects.order_by('complain').values('complain').annotate(
        count=Cast(((Count('complain') / 0.1 ) / cavg) / 0.1, FloatField()))

    vvctr = Visitor.objects.filter(purpose='Vacation').count()
    vodctr = Visitor.objects.filter(purpose='One_Day').count()
    vonctr = Visitor.objects.filter(purpose='Overnight').count()
    vectr = Visitor.objects.filter(purpose='Event').count()
    vpgctr = Visitor.objects.filter(purpose='Pool_Gym').count()

    vavg = vvctr + vodctr + vonctr + vectr + vpgctr
    vfloat = Visitor.objects.order_by('purpose').values('purpose').annotate(
        count=Cast(((Count('purpose') / 0.1) / vavg) / 0.1, FloatField()))

    cfq = Complaint.objects.values('complain').order_by().annotate(c_count=Cast(((Count('complain')/ 0.1) / cavg) / 0.1, FloatField()))
    cfmax = max(cfq, key=lambda x: x['c_count'])
    cfq2 = Complaint.objects.values('complain').order_by().annotate(c_count2=Count('complain'))
    cfmax2 = max(cfq2, key=lambda x: x['c_count2'])

    vfq = Visitor.objects.values('purpose').order_by().annotate(v_count=Cast(((Count('purpose') / 0.1) / vavg) / 0.1, FloatField()))
    vfmax = max(vfq, key=lambda x: x['v_count'])
    vfq2 = Visitor.objects.values('purpose').order_by().annotate(v_count2=Count('purpose'))
    vfmax2 = max(vfq2, key=lambda x: x['v_count2'])

    uctr = User.objects.all().extra({'date_joined': "date(date_joined)"}).values('date_joined').\
        annotate(created_count=Count('id'))
    ulctr = User.objects.all().extra({'last_login': "date(last_login)"}).values('last_login'). \
        annotate(log_count=Count('id'))

    ufq = User.objects.values('last_login').order_by().annotate(
        u_count=Cast(((Count('last_login') / 0.1) / uctr2) / 0.1, FloatField()))
    ufmax = max(ufq, key=lambda x: x['u_count'])

    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    args = {'user':request.user, 'info_tenant_id': request.user.tenant.id, 'vfmax':vfmax, 'vfmax2':vfmax2, 'ufmax':ufmax,
            'tctr': tctr,'cctr': cctr, 'bctr': bctr, 'vctr': vctr, 'cfloat':cfloat, 'cfmax':cfmax, 'cfmax2':cfmax2,
            'cmctr': cmctr, 'csctr': csctr, 'cnctr': cnctr,'cpcctr': cpcctr, 'uctr':uctr, 'uctr2':uctr2, 'ulctr':ulctr,
            'cpctr': cpctr, 'cscctr': cscctr, 'cbctr': cbctr, 'coctr': coctr, 'vfloat':vfloat,'notif': notif,
            'bill_include': bill_include, 'visit_include': visit_include,
            'vvctr':vvctr, 'vodctr':vodctr, 'vonctr':vonctr, 'vectr':vectr, 'vpgctr':vpgctr,
            }
    return render(request,'information/analytics.html',args)


def billings(request):
    tid = request.user.tenant.id
    bills = Billing.objects.filter(info_tenant=tid, status='Pending') | Billing.objects.filter(info_tenant=tid, status='Processing')

    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    args = {'user':request.user, 'info_tenant_id':request.user.tenant.id, 'bills':bills, 'notif':notif,
            'bill_include':bill_include, 'visit_include':visit_include,}
    return render(request,'information/billings.html',args)


def billings_p(request):
    tid = request.user.tenant.id
    bills = Billing.objects.filter(info_tenant=tid, status='Paid')

    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    args = {'user':request.user, 'info_tenant_id':request.user.tenant.id, 'bills':bills, 'notif':notif,
            'bill_include':bill_include, 'visit_include':visit_include,}
    return render(request,'information/billings_p.html',args)


def visitors(request):
    form = VisitorForm(initial={'status': 'Pending'})
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        unit = request.user.tenant.unit
        tenant = Tenant.objects.get(unit=unit)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.info_tenant = tenant
            comp.save()

            messages.success(request, 'Visitor Request successfully submitted.')
            return redirect('/information/visitors')

    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    context = {'form': form, 'info_tenant_id': request.user.tenant.id, 'notif':notif,
                'bill_include':bill_include, 'visit_include':visit_include,}
    return render(request, 'information/visitors.html', context)


def visitors_history(request):
    tid = request.user.tenant.id
    visitor = Visitor.objects.filter(info_tenant=tid)

    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    args = {'user':request.user, 'info_tenant_id':request.user.tenant.id, 'visitor':visitor, 'notif':notif,
            'bill_include':bill_include, 'visit_include':visit_include,}
    return render(request,'information/visitors_h.html',args)


def complaints(request):
    form = ComplaintForm()
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        unit = request.user.tenant.unit
        tenant = Tenant.objects.get(unit=unit)
        if form.is_valid():
            comp = form.save(commit=False)
            comp.info_tenant = tenant
            comp.save()
            messages.success(request, 'Complaint successfully submitted.')
            return redirect('/information/complaints')

    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    context = {'form': form, 'info_tenant_id': request.user.tenant.id, 'notif':notif,
            'bill_include':bill_include, 'visit_include':visit_include,}
    return render(request, 'information/complaints.html', context)


def complaints_history(request):
    tid = request.user.tenant.id
    complaint = Complaint.objects.filter(info_tenant=tid)

    unit = request.user.tenant.unit
    tenant = Tenant.objects.get(unit=unit)
    bill_include = 'billing'
    visit_include = 'visitor'
    notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
            | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

    args = {'user':request.user, 'info_tenant_id':request.user.tenant.id, 'complaint':complaint, 'notif':notif,
            'bill_include':bill_include, 'visit_include':visit_include,}
    return render(request,'information/complaints_h.html',args)


def settings(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account successfully updated.')
            return redirect('/information/settings')
    else:
        form = UserUpdateForm(instance=request.user)

        unit = request.user.tenant.unit
        tenant = Tenant.objects.get(unit=unit)
        bill_include = 'billing'
        visit_include = 'visitor'
        notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

        args = {'form': form, 'user':request.user.username, 'first_name':request.user.first_name, 'last_name':request.user.last_name,
                'email':request.user.email, 'notif':notif, 'bill_include':bill_include, 'visit_include':visit_include,}
        return render(request, 'information/settings.html', args)


def settings_pass(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password successfully updated.')
            return redirect('/information/login')
    else:
        form = PasswordChangeForm(user=request.user)

        unit = request.user.tenant.unit
        tenant = Tenant.objects.get(unit=unit)
        bill_include = 'billing'
        visit_include = 'visitor'
        notif = LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Paid') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Processing') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Pending') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Approved') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Declined') \
                | LogEntry.objects.filter(object_repr__startswith=tenant, object_repr__contains='Done')

        args = {'form': form, 'notif':notif, 'bill_include':bill_include, 'visit_include':visit_include,}
        return render(request, 'information/settings_pass.html', args)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        tenant_form = TenantForm(request.POST)
        if form.is_valid() and tenant_form.is_valid():
            user = form.save()
            tenant = tenant_form.save(commit=False)

            tenant.user = user
            tenant.save()

            messages.success(request, 'Tenant Account successfully created.')
            return redirect('/information/login')
    else:
        form = RegistrationForm()
        tenant_form = TenantForm()
        args = {'form': form, 'tenant_form': tenant_form}
        return render(request, 'information/reg_form.html',args)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Account successfully logged in.')
            return redirect('/information/profile')
        else:
            messages.warning(request, 'Username/Password is incorrect')
    return render(request, 'information/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('/information/login')
