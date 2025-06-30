# EncryptedFS: Sistema de Arquivos Criptografado com FUSE

Este projeto é uma implementação de um sistema de arquivos em userspace (FUSE) escrito em Python. Sua principal característica é que todos os dados de arquivos são armazenados de forma criptografada na memória, oferecendo uma camada de segurança e privacidade para o conteúdo dos arquivos.

## Visão Geral

O `EncryptedFS` utiliza a biblioteca `fusepy` para se integrar ao sistema operacional como um diretório montado. Todo o conteúdo gravado nos arquivos dentro deste diretório é criptografado em tempo real antes de ser armazenado na memória. Da mesma forma, ao ler um arquivo, seu conteúdo é descriptografado de forma transparente para o usuário.

A criptografia é simétrica e gerenciada pela biblioteca `cryptography`, utilizando o robusto algoritmo Fernet.

## Características

* **Sistema de Arquivos em Memória:** Todos os arquivos e seus conteúdos são mantidos na memória RAM. **Isso significa que todos os dados são voláteis e serão perdidos quando o sistema de arquivos for desmontado.**
* **Criptografia Transparente:** As operações de criptografia e descriptografia são automáticas e transparentes para o usuário final e para as aplicações.
* **Geração Automática de Chave:** Na primeira execução, uma chave de criptografia segura (`secret.key`) é gerada e salva no diretório onde o script foi iniciado.
* **Logging:** Todas as operações de criptografia e descriptografia são registradas no arquivo `log.txt` para fins de depuração.
* **Portabilidade:** Sendo escrito em Python, pode ser executado em diversos sistemas operacionais que suportam FUSE (como Linux e macOS).

## Requisitos

Para executar este projeto, você precisará de:

* Python 3.x
* Bibliotecas Python: `fusepy` e `cryptography`.

## Instalação e Uso

Siga os passos abaixo para montar e utilizar o sistema de arquivos criptografado.

**1. Clone ou Faça o Download do Repositório**

Primeiro, obtenha os arquivos do projeto (`encrypted_fs.py` e `crypto_utils.py`) e salve-os em um diretório de sua escolha.

```bash
# Exemplo usando git
git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>
```

**2. Instale as Dependências**

Use o gerenciador de dependências `poetry` para instalar as bibliotecas necessárias.

```bash
# Instala as bibliotecas fusepy e cryptography
poetry install
```

**3. Crie um Ponto de Montagem**

Este é o diretório onde seu sistema de arquivos criptografado ficará acessível.

```bash
mkdir /tmp/encrypted_fs
```

**4. Execute o Sistema de Arquivos**

No diretório onde estão os scripts, execute o `encrypted_fs.py`, passando o ponto de montagem como argumento.

```bash
python3 encrypted_fs.py /tmp/encrypted_fs
```

* Na primeira vez que você executar, os arquivos `secret.key` (sua chave de criptografia) e `log.txt` serão criados no diretório atual.
* O terminal ficará ocupado, exibindo logs em tempo real. **Deixe este terminal aberto.**

**5. Utilize o Sistema de Arquivos**

**Abra um novo terminal** e comece a usar o diretório montado como qualquer outro.

```bash
# Navegue até o diretório montado
cd /tmp/encrypted_fs

# Crie um arquivo (o conteúdo será criptografado em memória)
echo "Este é um texto secreto!" > meu_arquivo_secreto.txt

# Liste os arquivos
ls -la

# Leia o arquivo (o conteúdo será descriptografado na leitura)
cat meu_arquivo_secreto.txt
# Saída: Este é um texto secreto!
```

**6. Para Desmontar**

Volte para o **primeiro terminal** (onde o script `encrypted_fs.py` está rodando) e pressione `Ctrl+C`. Isso encerrará o processo e desmontará o sistema de arquivos de forma segura.

## Aviso Importante

* **Proteja sua `secret.key`!** Se você perder este arquivo, não será possível descriptografar os dados existentes (caso você adaptasse o projeto para armazenamento persistente).
* Lembre-se que esta implementação padrão é **volátil**. Todos os dados serão perdidos ao desmontar o sistema de arquivos.