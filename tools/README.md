# 🛠️ Ferramentas de Tradução e Empacotamento — `tools/`

Este diretório contém os scripts Python usados para:

- **Validar** arquivos traduzidos da comunidade.
- **Empacotar** os arquivos `.lua` traduzidos no formato `.g` que pode ser usado dentro do jogo **Eastward**.

---

## 📦 Requisitos

- Python **3.10+**
- [Pipenv](https://pipenv.pypa.io/en/latest/) (para gerenciamento de dependências)
- Git (opcional, mas recomendado para clonar o projeto)

---

## 🔧 Instalação

### 1. Clone o repositório (se ainda não tiver feito)

```bash
git clone https://github.com/seu-usuario/eastward-ptbr.git
cd eastward-ptbr/tools
````

### 2. Instale o Pipenv (caso ainda não tenha)

```bash
pip install pipenv
```

> Se estiver usando Python via pyenv, conda ou brew no macOS/Linux, verifique se `pipenv` está no mesmo ambiente do Python 3.10+

### 3. Instale as dependências

Dentro da pasta `tools/`:

```bash
pipenv install
```

---

### ▶️ Como usar via `script.py`

Este projeto oferece uma interface de linha de comando unificada para empacotar, desempacotar e validar traduções com o arquivo `tools/script.py`.

#### 📦 Empacotar traduções (`--pack`)

Gera um novo arquivo `.g` a partir dos arquivos traduzidos na pasta `raw`:

```bash
python tools/script.py --pack ./build/locale.g ./raw
```

#### 📂 Desempacotar arquivo original (`--unpack`)

Extrai os arquivos `.lua` do `.g` original para uma pasta:

```bash
python tools/script.py --unpack ./build/locale.g ./test2
```

#### ✅ Validar traduções (`--validate`)

Valida os arquivos traduzidos comparando com os arquivos originais extraídos:

```bash
python tools/script.py --validate ./tools/files/original.g ./raw
```


## 📘 Dicas
Rode com `--help` para ver todas as opções:

```bash
python tools/script.py --help
```

* Rode `pipenv shell` para entrar no ambiente virtual interativo.
* Use `pipenv install <pacote>` para adicionar novas dependências.

* Para entrar no ambiente virtual após tudo configurado, pode ser utilizado o comando `python -m pipenv shell`