from dataclasses import dataclass
import random
import multiprocessing as mp

bank_list = {}

class Env():
  def __init__(self, budget):
   
    self.budget = budget

    @property
    def budget(self):
      print('Budżet to: ')
      return self._budget
    
    @budget.setter
    def budget(self, budget):
      if budget > 0:
        self._budget = budget
      else: 
        raise ValueError()

  @staticmethod
  def transfer(client1, client2, sum):
    if sum >= 0:
        if sum <= client1.money:
          client1.money -= sum
          client2.money += sum
    else:
        if sum <= client2.money:
          client1.money += sum
          client2.money -= sum

  @classmethod
  def change_bank(cls, client, bank):
    if client.bank_name != bank.bank_name and client.credit == 0 :
      bank_list[client.bank_name].client_list.remove(client)
      client.bank_name = bank.bank_name
      bank.client_list.append(client)


class Bank(mp.Process):
  def __init__(self, bank_name, budget):
    self.client_list = []
    self.bank_name = bank_name
    bank_list[bank_name] = self
    super(Bank, self).__init__()
    self.credit_limit = budget/2
    self.budget = budget

    @property
    def budget(self):
      return self._budget
    
    @budget.setter
    def budget(self, budget):
      if budget > 0:
        self._budget = budget
      else: 
        raise ValueError()
 
  def new_client(self, client):
    self.client_list.append(client)
    client.bank_name = self.bank_name
  
  def transfer(self, client1, client2, sum):
    if client1.bank_name == client2.bank_name == self.bank_name:
      if sum >= 0:
        if sum <= client1.money:
          client1.money -= sum
          client2.money += sum
      else:
        if sum <= client2.money:
          client1.money += sum
          client2.money -= sum
    else:
      Env.transfer(client1, client2, sum)

  
  def cash_input(self, client, sum):
    if client in self.client_list:
      client.money += sum

  def cash_withdrawal(self, client, sum):
    if client in self.client_list and client.money >= sum:
      client.money -= sum
      return True

  def credit(self, client, sum):
    if sum >= 0 and client.credit == 0:
      if client.bank_name == self.bank_name and sum <= 10*client.money and sum <= self.credit_limit:
        client.credit = sum
        self.credit_limit -= sum
        client.money += sum
        return True
      else:
        return False  
    elif client.bank_name == self.bank_name and sum < 0 and client.credit != 0 and sum <= client.money:
        client.credit += sum
        client.money -= sum
        self.credit_limit += sum
        return True
    else:
      return False

  def delete_account(self, client):
    if client.credit == 0 and client.bank_name == self.bank_name:
      self.client_list.remove(client)
      client.bank_name = ''


@dataclass
class Client:   
  name: str
  last_name: str
  money: float
  bank_name: str = ''
  credit: float = 0


if __name__ == "__main__":
  bank1 = Bank('bank1', 100000)
  bank1.start()
  bank1.join()
  bank2 = Bank('bank2', 150000)
  bank2.start()
  bank2.join()
  bank3 = Bank('bank3', 200000)
  bank3.start()
  bank3.join()
   
  names = ['Luke','Anna', 'Tomasz', 'Kamil', 'Agnieszka', 'Julian', 'Zoltan', 'Arwena']
  last_names = ['Smith','Nowak', 'Smith', 'Skywalker', 'Page', 'Kowal', 'Drue']
  clients = [Client(names[random.randint(0, len(names)-1)], last_names[random.randint(0, len(last_names)-1)], random.randint(1000,20000)) for i in range(12)]

  for client in clients:
    random.choice(list(bank_list.values())).new_client(client)
  
  print('\nTransfers')
  for i in range(4):
    client1 = random.choice(clients)
    client2 = random.choice(clients)
    ammount = random.randint(-2000,2000)
    name1 = client1.name + ' ' + client1.last_name
    name2 = client2.name + ' ' + client2.last_name
    
    print('{} has {}, {} has {}, transaciotn sum will be {}'.format(name1, client1.money, name2, client2.money, ammount))
    Env.transfer(client1,client2,ammount)
    print('Transaction ended. Client 1 has {}, clinet 2 has {}'.format(client1.money, client2.money))

  print('\nDeposit')
  for i in range(3):
    bank = random.choice(list(bank_list.values()))
    client = random.choice(bank.client_list)
    ammount = random.randint(0,10000)
    print('Customer has {}, he/she will input {}'.format(client.money,ammount))
    bank.cash_input(client, ammount)
    print('Customer has {} after deposit'.format(client.money))

  print('\nWithdrawal')
  for i in range(3):
    bank = random.choice(list(bank_list.values()))
    client = random.choice(bank.client_list)
    ammount = random.randint(0,10000)
    print('Customer has {}, wants to withdraw {}'.format(client.money,ammount) )
    if bank.cash_withdrawal(client, ammount):
      print('Customer has {} after withdrawal'.format(client.money))
    else:
      print("Customer didn't have enought money")

  print('\nCredits')
  for i in range(3):
    bank = random.choice(list(bank_list.values()))
    client = random.choice(bank.client_list)
    ammount = random.randint(0,10000)
    print('Customer has {}, wants to take {} in credit'.format(client.money,ammount) )
    if bank.credit(client, ammount):
      print('Customer has {} after taking credit'.format(client.money))
    else:
      print("Customer wanted to much. Credit denied")

  print('\nBank change')
  for i in range(3):
    bank1 = random.choice(list(bank_list.values()))
    bank2 = random.choice(list(bank_list.values()))
    while bank1 == bank2:
      bank2 = random.choice(list(bank_list.values()))

    client = random.choice(bank1.client_list)

    print('Client want to change bank from {} to {}'.format(client.bank_name, bank2.bank_name))
    Env.change_bank(client, bank2)
    if client in bank2.client_list:
      print('Bank changed to {}'.format(client.bank_name))
    elif client.credit != 0:
      print("Couldn't change bank because of credit") 

  print('\nDelete account')
  for i in range(3):
    bank = random.choice(list(bank_list.values()))
    client = random.choice(bank.client_list) 

    print('Client wants to delete account in {}'.format(bank.bank_name))
    bank.delete_account(client)
    if client in bank.client_list and client.credit != 0:
      print("Couldn't delete because of credit")
    elif client.bank_name == '' and client not in bank.client_list:
      print('Account deleted')