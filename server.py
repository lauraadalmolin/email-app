from audioop import add
from _thread import *
import threading
import socket
import secrets

class Account:
    def __init__(self, email:str, password:str):
        self.email = email
        self.password = password
        self.received = []
        self.sent = []

class Message:
    def __init__(self, subject:str, content:str, recipient:str, author:str):
        self.subject = subject
        self.content = content
        self.recipient = recipient
        self.author = author

    def __str__(self):
        return '%s;%s;%s;%s' % (self.subject, self.content, self.recipient, self.author)

admin = Account('do-not-reply@pinemail.com', '123456')

accounts = {}
accounts['do-not-reply@pinemail.com'] = admin

authenticatedUsers = {}
 
"""
Função que cria uma nova conta
Retorno:
    feedbackString;authToken
authToken é None quando não é criada a conta
"""
def newAccount(email, password):
    
    if email in accounts:
        return "The email provided is not available;None"
    
    account = Account(email, password)
    accounts[email] = account
    
    token = secrets.token_hex(16)
    authenticatedUsers[token] = email

    return "Account created;{:s}".format(token)

"""
Função que realiza o login na conta
Retorno:
    feedbackString;authToken
authToken é None quando o usuário não é logado
"""
def login(email, password):

    if email not in accounts:
        return "Email not found;None"

    account = accounts[email]
    if account.password == password:
        token = secrets.token_hex(16)
        authenticatedUsers[token] = email

        return "Welcome;{:s}".format(token)
    else:
        return "Incorrect password;None"

def logout(token, email):
    authenticatedUsers.pop(token)

"""
Função responsável pela leitura leitura do email
    option pode ser received ou sent
    retorna array com todas as mensagens da caixa escolhida (received ou sent)
    o formato de cada objeto do array é Message
"""
def getMessages(option, email):
    messages = getattr(accounts[email], option)
    
    if len(messages) == 0:
        return None
 
    messagesAsStr = ""
    for element in messages:
        messagesAsStr = messagesAsStr + "¬" + str(element)

    messagesAsStr = messagesAsStr.strip('¬')

    return messagesAsStr


"""
Função responsável pelo envio de menssagens
    verifica se o recipient existe
    caso não exista, gera mensagem de erro para o sender
    caso exista, envia a mensagem para o recipient
    por fim, retorna as mensagens da caixa de entrada
"""
def sendMessage(recipient, subject, content, senderEmail):
    message = Message(subject, content, recipient, senderEmail)
    accounts[senderEmail].sent.append(message)

    if recipient not in accounts:
        errorSubject = 'Recipient not found for: ' + subject
        errorContent = 'The message was not delivered because the recipient was not found.'
        
        errorMessage = Message(errorSubject, errorContent, senderEmail, admin.email)
        accounts[senderEmail].received.append(errorMessage)
    else:
        accounts[recipient].received.append(message)
    
    return getMessages('received', senderEmail)

"""
Função que exclui um email
    recebe uma option, que pode ser received ou sent
    remove o email no index informado
    retorna uma string com o status da mensagem
"""
def delete(option, index, email):
    index = int(index)
    if option == "received":
        if index >= len(accounts[email].received) or index < 0:
            return "Could not find message"
        else:
            del(accounts[email].received[index])
            return "Operation successful!"
    else:
        if index >= len(accounts[email].sent) or index < 0:
            return "Could not find message"
        else:
            del(accounts[email].sent[index])
            return "Operation successful!"


noAuthFns = {'login': login, 'newAccount': newAccount}
authFns = {'delete': delete, 'sendMessage': sendMessage, 'getMessages': getMessages, 'logout': logout }

# Constantes que compõem o socket (Host e porta)
host = "localhost"
door = 8000

#Aqui é invocado o método socket do objeto socket, os parâmetros são a família de protocolos e tipo de socket
server = socket.socket()
server.bind((host, door))

server.listen(5)

def on_new_client(connection, address):

    while True:

        bytedata = connection.recv(2048)
        data = bytedata.decode('utf-8')

        if not data:
            continue

        if data == 'exit':
            connection.close()
            break

        params = data.split(';')
        fnName = params[0]
        del(params[0])

        print('-> Function called: {:s}'.format(fnName))

        if fnName in noAuthFns:
            output = noAuthFns[fnName](*params)
            connection.send(output.encode())
            print('<- Output sent: ', output)
        else:
            token = params[0]
            del(params[0])

            authEmail = authenticatedUsers[token]

            if authEmail == None:
                output = 'Invalid token!'
                connection.send(output)
                print('<- Output sent: ', output)

            else:
                if params == []:
                    output = authFns[fnName](token, authEmail)
                else:
                    output = authFns[fnName](*params, authEmail)
                
                connection.send(repr(output).encode())
                print('<- Output sent: ', output)


"""
Função principal
"""
def main():
    while True:
        print("Waiting for connection...")

        connection, address = server.accept()
        
        print("Connecting in {}".format(address))

        start_new_thread(on_new_client, (connection, address))

main()
