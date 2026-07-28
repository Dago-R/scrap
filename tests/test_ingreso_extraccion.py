"""Tests for dashboard/ingreso_extraccion.py — Punto 1, 4."""
from dashboard.ingreso_extraccion import _comentarios_desde_lista, _num_confianza


class TestComentariosDesdeLista:
    def test_propaga_emocion_y_tema_sugerido(self):
        entrada = [{"texto": "x", "emocion": "enojo", "tema_sugerido": "baches"}]
        result = _comentarios_desde_lista(entrada)
        assert len(result) == 1
        assert result[0]["texto"] == "x"
        assert result[0]["emocion"] == "enojo"
        assert result[0]["tema_sugerido"] == "baches"
        assert result[0]["confianza"] == "seguro"

    def test_propaga_confianza_emocion(self):
        entrada = [{"texto": "y", "emocion": "alegria", "confianza_emocion": "seguro"}]
        result = _comentarios_desde_lista(entrada)
        assert result[0]["confianza_emocion"] == "seguro"

    def test_campos_ausentes_se_omiten(self):
        entrada = [{"texto": "z"}]
        result = _comentarios_desde_lista(entrada)
        assert "emocion" not in result[0]
        assert "tema_sugerido" not in result[0]
        assert "confianza_emocion" not in result[0]

    def test_campos_none_se_omiten(self):
        entrada = [{"texto": "w", "emocion": None, "tema_sugerido": None}]
        result = _comentarios_desde_lista(entrada)
        assert "emocion" not in result[0]
        assert "tema_sugerido" not in result[0]

    def test_campos_vacios_se_omiten(self):
        entrada = [{"texto": "v", "emocion": "", "tema_sugerido": "  "}]
        result = _comentarios_desde_lista(entrada)
        assert "emocion" not in result[0]
        assert "tema_sugerido" not in result[0]

    def test_lista_vacia(self):
        assert _comentarios_desde_lista([]) == []

    def test_none_entrada(self):
        assert _comentarios_desde_lista(None) == []


class TestNumConfianza:
    def test_none_retorna_no_detectado(self):
        assert _num_confianza(None) == {"valor": None, "confianza": "no_detectado"}

    def test_dict_con_valor(self):
        assert _num_confianza({"valor": 42, "confianza": "seguro"}) == {"valor": 42, "confianza": "seguro"}

    def test_entero_directo(self):
        assert _num_confianza(42) == {"valor": 42, "confianza": "seguro"}
