# ![Marquinhos](images/dj.bmp) DJ Marquinhos


DJ Marquinhos é um bot para Discord feito em Python que toca músicas diretamente do YouTube. Ele permite que os usuários adicionem músicas a uma fila e curtam suas faixas favoritas sem sair do servidor do Discord.

## Recursos
- Reproduz músicas do YouTube ou link MP3
- Reproduz músicas MP3 por anexo
- Gerencia uma fila de músicas
- Suporte a múltiplos servidores

## Requisitos
Antes de instalar o DJ Marquinhos, certifique-se de que você tem os seguintes requisitos:
- Python 3.2 ou superior
- Ter `ffmpeg` instalado e configurado no sistema
- Um bot do Discord criado no [developer portal](https://discord.com/developers/applications/)
- **Você também precisa [gerar um token de autenticação do YouTube para o seu bot](https://pytubefix.readthedocs.io/en/latest/user/auth.html)** 

## Instalação
1. Clone este repositório:
   ```sh
   git clone https://github.com/Brunnexo/dj-marquinhos.git
   cd dj-marquinhos
   ```
2. Crie um ambiente virtual:
   ```sh
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   - No Windows:
     ```sh
     venv\Scripts\activate
     ```
   - No macOS/Linux:
     ```sh
     source venv/bin/activate
     ```
4. Instale as dependências:
   ```sh
   pip install -r requirements.txt
   ```
5. Defina a variável de ambiente com o token do bot:
   - No Windows (PowerShell):
     ```sh
     $env:DJ_DISCORD_TOKEN="seu_token_aqui"
     ```
   - No macOS/Linux:
     ```sh
     export DJ_DISCORD_TOKEN="seu_token_aqui"
     ```
   - No Linux com /etc/environment
     ```
     DJ_DISCORD_TOKEN=seu_token_aqui (sem aspas)
     ```
6. Execute o bot:
   ```sh
   python main.py
   ```

## Comandos principais
- `/help` - Exibir a lista de comandos
- `/play <url>` - Reproduz uma música do YouTube ou MP3
- `/pause` - Pausa a reprodução
- `/resume` - Retoma a música pausada
- `/skip` - Pula para a próxima música da fila
- `/queue` - Exibe a lista de músicas na fila
- `/stop` - Para a reprodução e limpa a fila
- `/keep` - Manter o bot no canal (*ou ele irá se desconectar após 60s*)

## Comando por anexo
- Anexe o arquivo MP3 e na mensagem mencione o bot acompanhado de `play` para tocar o arquivo

## Funcionalidades a Implementar
- 🔲 Capacidade de reproduzir streams
- 🔲 Função de busca de títulos
- ❎ <s>Comandos personalizados por servidor</s> (não faz sentido!)
- ✅ Rodar no Raspberry Pi (2, 3, 4)

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).
