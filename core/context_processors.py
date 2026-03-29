from cadastros.config import CADASTRO_CONFIG


def sidebar_cadastros(request):
    return {"sidebar_cadastros": CADASTRO_CONFIG}
