from django.contrib import admin, auth
from django.contrib.auth.models import Group
from .models import Visitor, Complaint, Billing, Tenant

admin.site.site_header = "Tenant Portal Admin Dashboard"


class VisitorAdmin(admin.ModelAdmin):
    list_display = ('get_tenant', 'date_issued', 'purpose', 'visitor_count', 'visitor_names', 'visit_date', 'duration', 'status')
    list_filter = ('purpose',)

    def get_tenant(self, obj):
        return obj.info_tenant.unit

    get_tenant.admin_order_field = 'tenant'  # Allows column order sorting
    get_tenant.short_description = 'Tenant Information'


class TenantAdmin(admin.ModelAdmin):
    list_display = ('get_account','unit','contact', 'work_address','birthday')
    list_filter = ('unit',)

    def get_account(self, obj):
        return obj.user.username,obj.user.email
    get_account.admin_order_field = 'username'  # Allows column order sorting
    get_account.short_description = 'Username'


class BillingAdmin(admin.ModelAdmin):
    list_display = ('get_tenant','date_issued','billing_type','billing_fee','due_date', 'status')
    list_filter = ('due_date',)

    def get_tenant(self, obj):
        return obj.info_tenant.unit
    get_tenant.admin_order_field = 'tenant'  # Allows column order sorting
    get_tenant.short_description = 'Tenant Information'


class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('get_tenant','date_issued','complain','elaborate','neighbour','staff','supporting_image')
    list_filter = ('complain',)

    def get_tenant(self, obj):
        return obj.info_tenant.unit
    get_tenant.admin_order_field = 'tenant'  # Allows column order sorting
    get_tenant.short_description = 'Tenant Information'


admin.site.register(Visitor, VisitorAdmin)
admin.site.register(Tenant, TenantAdmin)
admin.site.register(Billing, BillingAdmin)
admin.site.register(Complaint, ComplaintAdmin)

admin.site.unregister(Group)


