from faker import Faker
import requests
from random import randint

fake = Faker('en_US')
user_port = 'http://localhost:8070'
underwriter_port = 'http://localhost:8071'
transaction_port = 'http://localhost:8073'
bank_port = 'http://localhost:8083'

def get_bearer():
    user_json = {
        "username": "blackEyeBeans",
        "password": "Abc123456*"
    }

    try:
        x = requests.post('http://localhost:8070/login', json=user_json)
    except requests.exceptions.ConnectionError:
        print("Connection error when getting bearer token")
        return None

    return x.headers['Authorization']

def create_applicant(key):

    address = fake.street_address()
    city = fake.city()
    state = fake.state()
    zipcode = fake.postalcode()
    firstName = fake.first_name()
    lastName = fake.last_name()
    email = fake.email()
    phone = fake.numerify(text='### ### ####')
    socialSecurity = fake.ssn()
    password = fake.password(length=10, upper_case=True, special_chars=True, digits=True)

    applicant_json = {
        'firstName': firstName,
        'lastName': lastName,
        'dateOfBirth': str(fake.date_of_birth(minimum_age=18)),
        'gender': 'UNSPECIFIED',
        'email': email,
        'phone': phone,
        'socialSecurity': socialSecurity,
        'driversLicense': fake.numerify(text='########'),
        'income': randint(1000000, 9000000),
        'address': address,
        'city': city,
        'state': state,
        'zipcode': zipcode,
        'mailingAddress': address,
        'mailingCity': city,
        'mailingState': state,
        'mailingZipcode': zipcode
        }

    try:
        applicant_request = requests.post(underwriter_port + '/applicants', json=applicant_json, headers={'Authorization': key})
    
    except requests.exceptions.ConnectionError:
        print("Connection error with applicant request")
        return None

    print(applicant_request.json())
    
    application_json = {
        'applicationType': "CHECKING",
        'noApplicants': True,
        'applicantIds': [applicant_request.json()['id']]
        }

    try:
        application_request = requests.post(underwriter_port + '/applications', json=application_json, headers={'Authorization': key})
    except requests.exceptions.ConnectionError:
        print("Connection error with application request")
        return None

    print(application_request.json())

    user_json = {
        'role': "member",
        'username': fake.user_name(),
        'password': password,
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'phone': phone,
        'membershipId': application_request.json()['createdMembers'][0]['membershipId'],
        'lastFourOfSSN': applicant_request.json()['socialSecurity'].split('-')[-1]
        }

    print("PASSWORD TEST", password)
    
    try:
        user_request = requests.post(user_port + '/users/registration', json=user_json)
    except requests.exceptions.ConnectionError:
        print("Connection error with user request")
        return None

    print(user_request.json())

    merchantCode = ''
    for x in range(0, 2):
        merchantCode += fake.random_uppercase_letter()

    merchantCode += fake.numerify(text='####')

    print("Merchant CODE TEST", merchantCode)

    transaction_json = {
        'type': "DEPOSIT",
        'method': "CREDIT_CARD",
        'amount': randint(10000, 500000),
        'merchantCode': merchantCode,
        'merchantName': fake.company(),
        'description': fake.sentence(nb_words=25),
        'accountNumber': application_request.json()['createdAccounts'][0]['accountNumber']
        }

    try:
        transaction_request = requests.post(transaction_port + '/transactions', json=transaction_json, headers={'Authorization': key})
    except requests.exceptions.ConnectionError:
        print("Connection error with transaction request")
        return None

    print(transaction_request.json())

    bankAddress = fake.street_address()
    bankCity = fake.city()
    bankState = fake.state()
    bankZipcode = fake.postalcode()


    bank_json = {
        'routingNumber': fake.numerify(text='#########'),
        'address': bankAddress,
        'city': bankCity,
        'state': bankState,
        'zipcode': bankZipcode
        }

    try:
        bank_request = requests.post(bank_port + '/banks', json=bank_json, headers={'Authorization': key})
    except requests.exceptions.ConnectionError:
        print("Connection Error with bank request")
        return None

    print(bank_request.json())

    branch_json = {
        'name': fake.company(),
        'phone': fake.numerify(text='### ### ####'),
        'address': bankAddress,
        'city': bankCity,
        'state': bankState,
        'zipcode': bankZipcode,
        'bankID': bank_request.json()['id']
        }

    try:
        branch_request = requests.post(bank_port + '/branches', json=branch_json, headers={'Authorization': key})
    except requests.exceptions.ConnectionError:
        print("Connection Error with branch request")
        return None

    print(branch_request.json())

def main():
    key = get_bearer()
    create_applicant(key)

if __name__ == "__main__":
    main()

