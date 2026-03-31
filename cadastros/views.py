from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from usuarios.permissions import ModuleAccessMixin

from .config import CADASTRO_CONFIG


class CadastroConfigMixin(ModuleAccessMixin, LoginRequiredMixin):
    required_module = "cadastros"

    def get_config(self):
        slug = self.kwargs.get("model_slug")
        if slug not in CADASTRO_CONFIG:
            raise Http404("Cadastro não encontrado.")
        return CADASTRO_CONFIG[slug]

    def get_model(self):
        return self.get_config()["model"]

    def get_form_class(self):
        return self.get_config()["form"]

    def get_success_url(self):
        return reverse("cadastros:list", kwargs={"model_slug": self.kwargs["model_slug"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cadastros"] = CADASTRO_CONFIG
        context["cadastro_title"] = self.get_config()["title"]
        context["cadastro_slug"] = self.kwargs.get("model_slug")
        configured_fields = self.get_config().get("list_fields")
        if configured_fields:
            resolved_fields = []
            field_map = {field.name: field for field in self.get_model()._meta.fields}
            for item in configured_fields:
                if isinstance(item, dict):
                    resolved_fields.append(item)
                elif item in field_map:
                    resolved_fields.append(
                        {
                            "name": item,
                            "label": field_map[item].verbose_name,
                        }
                    )
            context["list_fields"] = resolved_fields
        else:
            context["list_fields"] = [
                {"name": field.name, "label": field.verbose_name}
                for field in self.get_model()._meta.fields
                if field.name != "id"
            ]
        return context


class CadastroIndexView(ModuleAccessMixin, LoginRequiredMixin, TemplateView):
    template_name = "cadastros/index.html"
    required_module = "cadastros"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cadastros"] = CADASTRO_CONFIG
        return context


class CadastroListView(CadastroConfigMixin, ListView):
    template_name = "cadastros/list.html"
    paginate_by = 20

    def get_queryset(self):
        return self.get_model().objects.all()


class CadastroCreateView(CadastroConfigMixin, CreateView):
    template_name = "cadastros/form.html"


class CadastroUpdateView(CadastroConfigMixin, UpdateView):
    template_name = "cadastros/form.html"

    def get_queryset(self):
        return self.get_model().objects.all()


class CadastroDeleteView(CadastroConfigMixin, DeleteView):
    template_name = "confirm_delete.html"

    def get_queryset(self):
        return self.get_model().objects.all()

# Create your views here.
