import unittest
from dataclasses import replace

from msen.services.homologacao_screener import (
    CriterioHomologado, ErroHomologacaoScreener, EstadoHomologacaoScreener,
    PERFIS_OBRIGATORIOS, validar_homologacao_screener,
)
from msen.validacao import criar_registro_criterios_producao


class TestHomologacaoScreener(unittest.TestCase):
    def setUp(self):
        definicoes = criar_registro_criterios_producao().listar()
        todos = {item.codigo for item in definicoes}
        self.padroes = set(sorted(codigo for codigo in todos if codigo.startswith("PAD_"))[:2])
        self.codigos = {codigo for codigo in todos if not codigo.startswith("PAD_")} | self.padroes
        criterios = tuple(CriterioHomologado(
            item.codigo, "APROVADO", item.assinatura_funcao, item.assinatura_regra,
            200, 200, 0, 0,
        ) for item in definicoes)
        self.estado = EstadoHomologacaoScreener(
            True, "ATUALIZADO", 3069, 3069, criterios,
            tuple((codigo, 3069) for codigo in sorted(PERFIS_OBRIGATORIOS)),
        )

    def erro(self, estado=None, codigos=None):
        with self.assertRaises(ErroHomologacaoScreener) as contexto:
            validar_homologacao_screener(
                estado or self.estado, codigos_carregados=self.codigos if codigos is None else codigos,
                codigos_padroes_selecionados=self.padroes,
            )
        return contexto.exception.codigo

    def test_aceita_somente_quadro_integralmente_aprovado(self):
        validar_homologacao_screener(
            self.estado, codigos_carregados=self.codigos,
            codigos_padroes_selecionados=self.padroes,
        )

    def test_bloqueia_estado_global_e_perfil_antigo(self):
        self.assertEqual("ALGORITMO_DESATUALIZADO", self.erro(replace(self.estado, atualizado=False)))
        self.assertEqual("PERFIS_DESATUALIZADOS", self.erro(replace(self.estado, quantidade_resultados=3068)))
        perfis = self.estado.perfis[:-1]
        self.assertEqual("PERFIS_DESATUALIZADOS", self.erro(replace(self.estado, perfis=perfis)))

    def test_bloqueia_funcao_nova_alterada_pendente_ou_com_n(self):
        original = self.estado.criterios[0]
        cenarios = (
            replace(original, assinatura_funcao="0" * 64),
            replace(original, estado="PENDENTE", aprovadas=0, pendentes=200),
            replace(original, estado="REPROVADO", aprovadas=199),
            replace(original, assinaturas_divergentes=1),
        )
        for criterio in cenarios:
            with self.subTest(criterio=criterio):
                estado = replace(self.estado, criterios=(criterio, *self.estado.criterios[1:]))
                self.assertEqual("FUNCAO_NAO_HOMOLOGADA", self.erro(estado))
        novo = CriterioHomologado("NOVO", "APROVADO", "a" * 64, "b" * 64, 200, 200, 0, 0)
        self.assertEqual("CATALOGO_DIVERGENTE", self.erro(replace(self.estado, criterios=(*self.estado.criterios, novo))))

    def test_bloqueia_filtro_ausente_ou_extra(self):
        self.assertEqual("COBERTURA_DIVERGENTE", self.erro(codigos=self.codigos - {"EST_SOMA"}))
        self.assertEqual("COBERTURA_DIVERGENTE", self.erro(codigos=self.codigos | {"EXTRA"}))


if __name__ == "__main__":
    unittest.main()
