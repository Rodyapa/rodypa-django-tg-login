from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from tg_authorization.admin_site.forms import LinkTGForm, UnLinkTGForm
from tg_authorization.admin_site.views import (LinkTGDoneView, LinkTGView,
                                               UnLinkTGView)
from tg_authorization.backends import TelegramIDBackend
from tg_authorization.errors import (NotTrustedTelegramData,
                                     OutdatedTelegramResponse)
from tg_authorization.verificators import verify_telegram_response
from tg_authorization.widgets.constructor import (create_callback_login_widget,
                                                  create_redirect_login_widget)


class TelegramAdminLoginMixin(AdminSite):
    '''Mixin for AdminSite instances.'''
    BOT_NAME = settings.TELEGRAM_AUTHENTICATION['BOT_NAME']
    BOT_TOKEN = settings.TELEGRAM_AUTHENTICATION['BOT_TOKEN']

    login_template = 'tg_login.html'
    user_can_tg_link = True

    def get_urls(self):
        """Add aditional urls for telegram login views."""
        urls = super().get_urls()
        custom_urls = [
            path('login/', (self.admin_login_view), name='admin_login'),
            path('login_via_tg', self.admin_tg_login_view, name='admin_tg_login')
        ]
        if self.user_can_tg_link is True:
            custom_urls.extend(
                (path(
                    'link_my_account',
                    self.add_tg_id_to_user,
                    name='admin_add_tg_id'
                ), path(
                    'link_tg_done', self.tg_link_done, name='link_tg_done'
                ), path(
                    'unlink_my_account', self.unlink_my_account, name='unlink_my_account'
                ), path(
                    'unlink_tg_done', self.tg_unlink_done, name='unlink_tg_done'
                ))
            )
        return custom_urls + urls

    def get_tg_link_element(self):
        """Return a html element of a link to page with telegram account linking."""
        tg_link_element = format_html(
            f'<a href="/{self.name}/link_my_account/">'
            f'link account to telegram </a>')
        return tg_link_element

    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for
        *every* page in the admin site.
        This redefinition also add telgram link.
        """
        each_context = super().each_context(request)
        if self.user_can_tg_link is True:
            each_context.update({
                'tg_link_element': self.get_tg_link_element()
            })
        return each_context

    def get_redirect_telegram_login_widget(self):
        """Get html element that will show redirect telegram login widget."""
        telegram_login_widget = create_redirect_login_widget(
            redirect_url=self.get_tg_redirect_url(),
            bot_name=self.BOT_NAME)
        return telegram_login_widget

    def get_callback_telegram_login_widget(self):
        """Get html element that will show callback telegram widget."""
        telegram_login_widget = create_callback_login_widget(
            bot_name=self.BOT_NAME)
        return telegram_login_widget

    def get_tg_redirect_url(self):
        """Get url on which telegram will respond after authorization."""
        redirect_url = (f'https://{settings.HOSTING_DOMAIN}'
                        f'/{self.name}/login_via_tg')
        return redirect_url

    def admin_login_view(self, request, extra_context=None):
        """Add new telegram login page, that allows to login via telegram."""
        new_context = {
            'telegram_login_widget': self.get_redirect_telegram_login_widget(),
        }
        if extra_context:
            new_context.update(extra_context)
        return LoginView.as_view(extra_context=new_context,
                                 template_name='tg_login.html')(request)

    def admin_tg_login_view(self, request, extra_content=None):
        """View that process response from telegram API. """
        # Check response from Telegram
        try:
            response_data = verify_telegram_response(
                bot_token=self.BOT_TOKEN,
                response_tg_data=request.GET
            )
        except NotTrustedTelegramData as e:
            pass
        # TODO Handle this exception and show it in a login form
        except OutdatedTelegramResponse as e:
            pass
        # TODO Handle this exception and show it in a login form
        if response_data:
            # Trying to authenticate with valid token:
            telegram_id = request.GET.get('id')
            user = TelegramIDBackend.authenticate(request=request, telegram_id=telegram_id)

            # if user was returned
            if user is not None:
                login(request, user, backend='tg_authorization.backends.TelegramIDBackend')
                return redirect(f'{self.name}:index')
            else:
                error_messages = {
                    'telegram_authentication_error': ('We do not have an existing account '
                                                      'corresponding to your telegram account')
                }
                return self.admin_login_view(request, extra_context=error_messages)

    def add_tg_id_to_user(self, request, extra_context=None):
        """Handle the 'link Django account with tg account task. """
        template = "admin/link_tg.html"

        new_context = {
            'telegram_login_widget': self.get_callback_telegram_login_widget(),
        }
        if extra_context:
            new_context.update(extra_context)

        url = reverse(f"{self.name}:link_tg_done", current_app=self.name)
        defaults = {
            "form_class": LinkTGForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(new_context or {})},
            "template_name": template,
        }
        request.current_app = self.name
        return LinkTGView.as_view(**defaults,)(request)

    def tg_link_done(self, request, extra_context=None):
        """ Display page after succeccsul telegram linking """
        template = "admin/link_tg_done.html"
        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        defaults["template_name"] = template
        request.current_app = self.name
        return LinkTGDoneView.as_view(**defaults)(request)

    def unlink_my_account(self, request, extra_context=None):
        """Handle the 'Unlink Django account from tg account task. """
        template = "admin/unlink_tg.html"

        url = reverse(f"{self.name}:unlink_tg_done", current_app=self.name)
        defaults = {
            "form_class": UnLinkTGForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
            "template_name": template,
        }
        request.current_app = self.name
        return UnLinkTGView.as_view(**defaults,)(request)

    def tg_unlink_done(self, request, extra_context=None):
        """ Display page after succeccsul telegram unlink."""
        template = "admin/unlink_tg_done.html"
        defaults = {
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        defaults["template_name"] = template
        request.current_app = self.name
        return UnLinkTGView.as_view(**defaults)(request)
