from django import forms

from .models import Banco, Cargo, CategoriaDeSpesa, Colaborador, FormaPagamento, Setor, SubcategoriaDeSpesa


class DateInput(forms.DateInput):
    input_type = "date"


def normalize_digits(value):
    return "".join(char for char in (value or "") if char.isdigit())


def is_valid_cpf(value):
    cpf = normalize_digits(value)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    for index in range(9, 11):
        total = sum(int(cpf[digit]) * ((index + 1) - digit) for digit in range(index))
        verifier = (total * 10) % 11
        verifier = 0 if verifier == 10 else verifier
        if verifier != int(cpf[index]):
            return False
    return True


def format_cpf(value):
    cpf = normalize_digits(value)
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ["nome"]


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ["nome"]


class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ["nome", "setor", "comissao_percentual"]


class ColaboradorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["documento"].label = "CPF"
        self.fields["documento"].help_text = "Informe um CPF valido."
        self.fields["documento"].widget.attrs.update({"placeholder": "000.000.000-00", "maxlength": "14", "inputmode": "numeric"})
        self.fields["cep"].help_text = "Ao informar um CEP valido, o endereco sera preenchido automaticamente."
        self.fields["cep"].widget.attrs.update({"placeholder": "00000-000", "maxlength": "9", "inputmode": "numeric"})
        self.fields["endereco"].widget.attrs.update({"placeholder": "Rua, avenida, travessa..."})
        self.fields["numero"].widget.attrs.update({"placeholder": "Numero"})
        self.fields["complemento"].widget.attrs.update({"placeholder": "Apartamento, bloco, referencia..."})
        self.fields["bairro"].widget.attrs.update({"placeholder": "Bairro"})
        self.fields["cidade"].widget.attrs.update({"placeholder": "Cidade"})
        self.fields["uf"].widget.attrs.update({"placeholder": "UF"})

    def clean_documento(self):
        documento = self.cleaned_data.get("documento", "")
        if not documento:
            return documento
        if not is_valid_cpf(documento):
            raise forms.ValidationError("Informe um CPF valido.")
        return format_cpf(documento)

    class Meta:
        model = Colaborador
        fields = [
            "nome",
            "cargo",
            "documento",
            "telefone",
            "email",
            "cep",
            "endereco",
            "numero",
            "complemento",
            "bairro",
            "cidade",
            "uf",
            "ativo",
            "data_admissao",
            "data_demissao",
        ]
        widgets = {"data_admissao": DateInput(), "data_demissao": DateInput()}


class FormaPagamentoForm(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = ["nome"]


class CategoriaDeSpesaForm(forms.ModelForm):
    class Meta:
        model = CategoriaDeSpesa
        fields = ["nome"]


class SubcategoriaDeSpesaForm(forms.ModelForm):
    class Meta:
        model = SubcategoriaDeSpesa
        fields = ["nome", "categoria"]
