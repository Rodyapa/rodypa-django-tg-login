from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from tg_authorization.admin_site.forms import LinkTGForm, UnLinkTGForm

UserModel = get_user_model()


class LinkTGView(FormView):
    form_class = LinkTGForm
    success_url = reverse_lazy("link_tg_done")
    template_name = "admin/link_tg.html"
    title = _("Link TG account")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class LinkTGDoneView(TemplateView):
    template_name = "admin/link_tg_done.html"
    title = _("Telegram linked successfully")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class UnLinkTGView(FormView):
    form_class = UnLinkTGForm
    success_url = reverse_lazy("unlink_tg_done")
    template_name = "admin/unlink_tg.html"
    title = _("Unlink TG account")

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UnLinkTGDoneView(TemplateView):
    template_name = "admin/unlink_tg_done.html"
    title = _("Telegram unlinked successfully")

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
