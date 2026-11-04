import tempfile
import unittest
from pathlib import Path
from repositorio import Repositorio

class TestarEstoque(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.banco = Repositorio(Path(self.temp.name))
        self.id = self.banco.cadastrar('Desinfetante', 10, 'operador')

    def tearDown(self):
        self.temp.cleanup()

    def test_cenario1_insuficiente(self):
        with self.assertRaisesRegex(ValueError, 'estoque insuficiente'):
            self.banco.movimentar(self.id, 'saida', 11, 'operador')
        self.assertEqual(self.banco.produto(self.id)['quantidade'], 10)
        self.assertEqual(len(self.banco.historico()), 1)

    def test_cenario2_saldo_exato(self):
        self.banco.movimentar(self.id, 'saida', 10, 'operador')
        self.assertEqual(self.banco.produto(self.id)['quantidade'], 0)
        self.assertEqual(self.banco.historico()[0]['usuario'], 'operador')

    def test_cenario3_saldo_parcial(self):
        self.banco.movimentar(self.id, 'saida', 4, 'admin')
        self.assertEqual(self.banco.produto(self.id)['quantidade'], 6)
        self.assertEqual(self.banco.historico()[0]['quantidade'], 4)
        self.assertTrue(self.banco.historico()[0]['data_hora'])

    def test_nome_e_paginacao(self):
        for n in range(6): self.banco.cadastrar(f'Papel {n}', 0, 'operador')
        lista, paginas, pagina = self.banco.produtos(nome='Papel', pagina=2)
        self.assertEqual((len(lista), paginas, pagina), (1, 2, 2))

if __name__ == '__main__': unittest.main()
