# ![Marquinhos](images/dj.bmp) DJ Marquinhos


DJ Marquinhos é um bot para Discord feito em Python que toca músicas diretamente do YouTube. Ele permite que os usuários adicionem músicas a uma fila e curtam suas faixas favoritas sem sair do servidor do Discord.

## Recursos
- Reproduz músicas do YouTube
- Reproduz músicas MP3 por anexo
- Gerencia uma fila de músicas
- Suporte a múltiplos servidores

## Requisitos
Antes de instalar o DJ Marquinhos, certifique-se de que você tem os seguintes requisitos:
- Python 3.2 ou superior
- `ffmpeg` instalado e configurado no sistema
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
6. Execute o bot:
   ```sh
   python main.py
   ```

## Comandos Principais
- `/play <url>` - Reproduz uma música do YouTube
- `/pause` - Pausa a reprodução
- `/resume` - Retoma a música pausada
- `/skip` - Pula para a próxima música da fila
- `/queue` - Exibe a lista de músicas na fila
- `/stop` - Para a reprodução e limpa a fila

## Funcionalidades a Implementar
- Capacidade de reproduzir streams
- Função de busca de títulos
- Comandos personalizados por servidor
- Rodar no Raspberry Pi Zero 2 (isso é pessoal)

## Contribuição
Fique à vontade para abrir issues e pull requests para melhorar o DJ Marquinhos!

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE).
