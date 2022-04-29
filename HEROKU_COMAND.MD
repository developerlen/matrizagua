COMO CRIAR DATABASE no HEROKU E LINKAR COM A SQLALCHEMY CRIADA LOCALMENTE

ADICIONAR POSTGRES:
1 - ir ao site keroku.com
2 - clicar na matriz pretendida
3 - no "overview", no Installed add-ons clickar "Configure Add-ons"
4 - Procurar "Postgres" e adicionar

LINKAR TUDO:
5 - Ir a "settings" e adicionar uma "Config Vars" intitulada SECRET_KEY. essa chave acho que pode ser aleatória, mas eu adicionei a que já tinha do sqlalchemy
6 - No "overview" clicar na base de dados que já criamos.
7 - Ai dá para ver que temos 0 TABLE, ainda não foi criada
8 - Clickar no Settings da database (settings diferente do passo 5)
9 - clickar em "view credentials"
10 - Copiar o URI para o nosso codigo.

O código fica então:

###############################

# pass antes definida para o alchemy, que coloquei no site do heroku

app.server.config['SECRET_KEY'] = '60b69ea75d65bfc586c4e778a9357219'

# URI copiado da nossa postgresql do heroku

app.server.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://jedcrkiqvpgghw:a55d8ab5271e0b58a11aa3f350384741181a593f53d5c4da6ccbd4fd2db74737@ec2-54-246-100-246.eu-west-1.compute.amazonaws.com:5432/da5crrdk573292'

No codigo é necessário ainda importar a biblioteca psycopg2 (não esquecer os requirements!)
##############################

CRIAR AS TABELAS
Com isto tudo construido, faz-se o deploy da app. Depois, com o cmd faz-se o login no heroku e cria-se a db, ou seja, a tabela:

```
heroku login
heroku run python --app NOME_DA_APP
from app import db
db.create_all()
```

Assim a tabela está criada.

QUERY DE DADOS

Na cmd:

```
heroku login
heroku run python --app NOME_DA_APP
from app import db
from app import Pessoas
Pessoas.query.all()
```

PARA APAGAR TUDO:

```
Pessoas.query.delete()
db.session.commit()
```

PARA CRIAR DF:

```
df = pd.read_sql('registo', con=db.engine)
```

(mas não dá para ler)

PARA CRIAR CSV DA TABELA TODA ('Basta alterar o nome da app e a pasta):
Abrir o cmd e escrever:

```
heroku login
heroku pg:psql --app NOME_DA_APP DATABASE
```

> > \COPY registo TO 'C:/Users/Vasco Abreu - PC/Documents/Python Projects/Matriz_Energia/db_registos/NOME.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);

comand para todas:

ENERGIA_PT:

heroku pg:psql --app matrizenergia DATABASE
\COPY registo TO 'C:/Users/Vasco Abreu - PC/Documents/Python Projects/Matriz_Energia/db_registos/energia_pt.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);

ENERGIA_EN:

heroku pg:psql --app matrizenergiaen DATABASE
\COPY registo TO 'C:/Users/Vasco Abreu - PC/Documents/Python Projects/Matriz_Energia/db_registos/energia_en.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);

AGUA_PT:

heroku pg:psql --app matrizagua DATABASE
\COPY registo TO 'C:/Users/Vasco Abreu - PC/Documents/Python Projects/Matriz_Agua/db_registos/agua_pt.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);

AGUA_EN:

heroku pg:psql --app matrizaguaen DATABASE
\COPY registo TO 'C:/Users/Vasco Abreu - PC/Documents/Python Projects/Matriz_Agua/db_registos/agua_en.csv' WITH (FORMAT csv, DELIMITER ',', HEADER true);
