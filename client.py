import socket

# Conecta no server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('0.0.0.0', 8000))

userData = []

"""
Função principal renderizada inicialmente.
Apresenta o menu inicial para o usuário criar uma conta ou realizar o login.
"""
def main():
  print("\n## Emails Service ##\n")
  print("1. New Account\n2. Login\n")

  option = 0
  while option not in range(1, 3):
    val = input("Enter the number of the desired option: ")
    try:
      option = int(val)
      if option == 1:
        signUp()
      elif option == 2:
        signIn()
      else:
        print("Invalid option\n")
    except:
      print("Invalid option\n")

"""
Função que envia as mensagens para o servidor (métodos e seus parâmetros)
e retorna o que recebeu do servidor caso a função não seja "logout".
"""
def sendServer(data):
  client.send(data.encode())
  if "logout" in data:
    return "Logout Success"
  else:
    bytedataFromServer = client.recv(2048)
    response = bytedataFromServer.decode('utf-8')
    return response

"""
Função que cria uma nova e se caso obter sucesso loga 
e chama outra função para listar as mensages recebidas do usuário logado.
"""
def signUp():
  print("\n--- Create new account ---")
  email = input("Email: ")
  password = input("Password: ")

  data = "newAccount;" + email + ";" + password
  resp = sendServer(data)
  resp = resp.split(";")

  if resp[1] != "None":
    userData.append(resp[1])
    getMessages("received")
  else:
    signUp()

"""
Função que loga o usuário no serviço, e se obter sucesso 
também lista as mensagens recebidas para o usuário.
"""
def signIn():
  print("\n--- Login ---")
  email = input("Email: ")
  password = input("Password: ")

  data = "login;" + email + ";" + password
  resp = sendServer(data)
  resp = resp.split(";")

  if resp[1] != "None":
    userData.append(resp[1])
    getMessages("received")
  else:
    print(resp[0])
    signIn()

"""
Função que recebe os dados das mensagens do servidor através do sendServer(),
e chama a função showMessages() para mostrar as mensagens no console.
"""
def getMessages(option):
  data = "getMessages;" + userData[0] + ";" + option
  resp = sendServer(data)

  print("\n--- " + option.capitalize() + " Messages ---")
  showMessages(option, resp)

  if option == "received":
    optionsAction(option, "sent")
  else:
    optionsAction(option, "received")

"""
Função que verifica se há alguma mensagem recebida do 
servidor e lista no console.
"""
def showMessages(option, resp):
  if resp == 'None':
    print("No messages")
  else:
    messages = resp.split("¬")
    for cont, message in enumerate(messages):
      data = message.split(";")
      print("\n(Message " + str(cont) + ")")
      print("Subject: " + data[0].strip('\''))
      print("Content: " + data[1])
      if option == "sent":
        print("Recipient: " + data[2])
      else:
        print("Author: " + data[3].strip('\''))
      cont += 1

"""
Função que tem como intuito mostrar o menu principal da aplicação no console.
Recebe a opção que o usuário informar e chama outra função de acordo com a opção escolhida.
"""
def optionsAction(currentList, otherList):
  print("\n0. Refresh {:s} Messages".format(currentList.capitalize()))
  print("1. Delete message\n2. " + otherList.capitalize() + " messages\n3. Send new message\n4. Logout\n")
  option = -1

  while option not in range(0, 5):
    val = input("Enter the number of the desired option: ")
    try:
      option = int(val)

      if option == 0:
        getMessages(currentList)
      if option == 1:
        deleteMessage(currentList)
      elif option == 2:
        getMessages(otherList)
      elif option == 3:
        sendMessage()
      elif option == 4:
        logout()
      else:
        print("Invalid option\n")
    except:
        print("Invalid option\n")

"""
Função que deleta as mensagens (enviadas ou recebidas).
Lê o index da mensagem que o usuário quer excluir, manda para o servidor e 
mostra novamente a caixa de mensagens em que o usuário estava.
"""
def deleteMessage(option):
  index = input("Enter the index of the message to be deleted: ")

  data = "delete;" + userData[0] + ";" + option + ";" + index
  resp = sendServer(data)
  print(resp)

  getMessages(option)

"""
Função que envia uma nova mensagem para outro usuário.
Recebe os dados da mensagem e envia para o servidor.
Ao enviar a caixa de entrada é apresentada novamente.
"""
def sendMessage():
  print("\n--- Send New Message ---")
  recipient = input("Recipient: ")
  subject = input("Subject: ")
  content = input("Content: ")

  data = "sendMessage;" + userData[0] + ";" + recipient + ";" + subject + ";" +  content
  resp = sendServer(data)

  print("\n--- Received Messages ---")
  showMessages("received", resp)

  optionsAction("received", "sent")
  
"""
Função que realiza o logout do usuário.
"""
def logout():
  data = "logout;" + userData[0]
  resp = sendServer(data)
  userData.pop()
  main()
  

main()
