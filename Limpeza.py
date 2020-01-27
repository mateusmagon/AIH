#!/usr/bin/env python
# coding: utf-8

# In[200]:


#importação dos pacotes necessários
import pandas as pd
import numpy as np
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
import seaborn as sns


# In[201]:


#carregamento do arquivo
aih = pd.read_csv('..\Dados\AIH AL 2017-2019.csv', low_memory = False)


# In[202]:


#Cria coluna paciente como string
Paciente = aih['id_paciente'].astype(str)
aih['Paciente'] = Paciente


# In[203]:


#gera informações sobre a tabela aih, uma vez que o método info não funcionou corretamente, acho que pelo grande número 
# de colunas
colunas = aih.columns
n_coluna, nome_coluna, Tipo_dado, Cont, nulos = [],[],[],[],[]
for i,col in enumerate(colunas):
    n_coluna.append(i+1)
    nome_coluna.append(col)
    Tipo_dado.append(aih[col].dtypes), 
    Cont.append(aih[col].count())
    nulos.append(np.count_nonzero(aih[col].isnull()))
    col_col = {'Nome da Coluna':nome_coluna,'Tipo de Dado': Tipo_dado,'Contagem' : Cont,'Nulos':nulos}
    df_colunas = pd.DataFrame(col_col,index = n_coluna)




# In[204]:


# exportando as informações das colunas como csv para que posssam ser mais bem visualizadas.
df_colunas.to_csv('..\Dados\colunas_aih.csv', index = True, sep =';')



# In[205]:


# selecionado as variáveis mais relevantes
aih_cam_pac = aih.loc[:,['id_paciente','Paciente','dt_internacao','dt_saida', 'co_cnes','no_fantasia', 'no_razao_social',
                         'sg_uf','nu_mun_hosp','no_municipio','nu_aih','nu_aih_prox','nu_aih_ant','desc_especialidade',
                         'ds_carater','ds_descricao','dt_paciente_nascimento','co_paciente_sexo','raca','co_cid_principal',
                         'ds_paciente_logr_bairro','co_paciente_logr_uf','co_paciente_logr_cep','co_cid_principal',
                         'no_cid_principal','co_procedimento_principal', 'procedimento_principal','cod_procedimento_secundario',
                         'desc_procedimento_secundario']]


# In[206]:


# agora o método info funciona! O campo CEP do paciente está todo nulificado, será excluído mais tarde.
aih_cam_pac.info()


# In[207]:


#transformar campos de data que estão em texto para o formato DateTime e inserí-los na tabela

dt_internacao = pd.to_datetime(aih_cam_pac['dt_internacao'], format= '%d/%m/%Y')
dt_saida = pd.to_datetime(aih_cam_pac['dt_saida'], format= '%d/%m/%Y')
dt_nascimento = pd.to_datetime(aih_cam_pac['dt_paciente_nascimento'], format = '%d/%m/%Y')
aih_cam_pac['dt_internacao'],aih_cam_pac['dt_saida'],aih_cam_pac['dt_paciente_nascimento'] = dt_internacao, dt_saida, dt_nascimento
aih_cam_pac.info()


# In[208]:


#conferindo os registros nulos no campo id_paciente. 17% do total dos registros estão com este campo nulo. Conferir se isto afeta a qualidade dos dados.
#gerando um csv também destes dados
aih_id_null = aih_cam_pac[aih_cam_pac['id_paciente'].isnull()== True]
aih_id_null.to_csv('..\Dados\pacientes_nulos.csv', index = True, sep =';')


# In[209]:


#excluindo a coluna CEP do logradouro que se encontra toda nulificada. Excluindo em seguida os valores nulos da 
# coluna id paciente

aih_sem_nulos = aih_cam_pac.drop(['co_paciente_logr_cep'], axis = 1)
aih_sem_nulos = aih_sem_nulos.dropna(how='any')
aih_sem_nulos = aih_sem_nulos.drop(['id_paciente'], axis = 1)


# In[210]:


#convertendo para os tipos de dados apropriados(strings e datas, no caso)
aih_sem_nulos['raca'].astype('category')
num = aih_sem_nulos[['co_cnes','nu_mun_hosp','nu_aih','nu_aih_prox','nu_aih_ant','co_procedimento_principal',
                     'cod_procedimento_secundario']].astype('str')
aih_sem_nulos[['co_cnes','nu_mun_hosp','nu_aih','nu_aih_prox','nu_aih_ant','co_procedimento_principal',
               'cod_procedimento_secundario']] = num[['co_cnes','nu_mun_hosp','nu_aih','nu_aih_prox','nu_aih_ant',
                'co_procedimento_principal','cod_procedimento_secundario']]


# In[211]:


#checando se todos os dados estão com os tipos corretos
aih_sem_nulos.info()
aih_sem_nulos.to_csv('..\Dados\_aih_sem_nulos.csv', index = True, sep =';')
 
 


# In[212]:


# Checando a coerência dos dados da coluna num_pacientes
num_pacientes = aih_sem_nulos.groupby('Paciente')['Paciente'].count().sort_values()
num_pacientes.head(10)


# In[213]:


# criando DataFrame para plotagem
num_pacientes = pd.DataFrame(data = num_pacientes)
num_pacientes.rename(columns={'Paciente': 'Contagem'}, inplace =True)
print(num_pacientes)


# In[214]:


# Plotando para melhor visualização da variável univariada. Considerei que cada contagem é um procedimento
sns.set_style('whitegrid')

hist, ax = plt.subplots()
ax = sns.distplot(num_pacientes['Contagem'],kde=False, color = 'green',bins=30,rug=False)
ax.set_title('Número de Procedimentos por Paciente')
ax.set_xlabel('Contagem Procedimentos')
ax.set_ylabel('Número de Pacientes')


# In[215]:


#checando um dos pacientes que possui dados discrepantes. O problema parece ser que cada paciente possui vários
#procedimentos na mesma data, 'inchando' a tabela
ex_pac_nulo = aih_sem_nulos[aih_sem_nulos['Paciente'] == '19944303300.0']
ex_pac_nulo.to_csv('..\Dados\exemplo_paciente_nulo.csv', index = True, sep =';')


# In[216]:


#Criando tabela multi-indexada por paciente e datas. Agrupando os dados de modo que as datas repetidas por inúmeros 
# procedimentos no mesmo dia sejam contados como uma só internação
aih_mult = aih_sem_nulos.loc[:,['Paciente','dt_internacao','procedimento_principal']]
aih_mult = aih_mult.groupby(['Paciente','dt_internacao']).count()
aih_mult.to_csv('..\Dados\_aih_mult.csv', index = True, sep =';')


# In[217]:


# Resetando o index da tabela  para permitir a contagem e o join com o restante das informações

aih_mult_flat = aih_mult.reset_index()


# In[218]:


#contando o número de pacientes com a tabela agora agrupada. os números parecem ter ficado mais coerentes. No final há 
# apenas 12870 registros únicos de pacientes
paciente_flat = aih_mult_flat.groupby('Paciente')['Paciente'].count().sort_values()
print(paciente_flat)


# In[219]:


#Só para confirmar o número de registros úncios de pacientes

len(aih_mult_flat['Paciente'].unique())



# In[220]:


#salvando para csv
aih_mult_flat.to_csv('..\Dados\_aih_mult_flat.csv', index = True, sep =';')
aih_mult_flat.info()



# In[232]:


#criando uma tabela mais específica com dados relevantes para a criação da 'Jornada do Paciente', fazendo uma 
#join. As variáveis selecionadas podem ser acrescentadas posteriormente

aih_jornada = aih_mult_flat.join(aih_sem_nulos[['no_fantasia','no_municipio','ds_paciente_logr_bairro']])
aih_jornada =aih_jornada.drop(['procedimento_principal'], axis = 1)
aih_jornada.info()


# In[233]:


# Só ajeitando a coluna 'paciente' para não ficar com o '.0' no final
paciente_s_zero = aih_jornada['Paciente'].str[:-2]
aih_jornada['Paciente'] = paciente_s_zero


# In[234]:


# Enviando o arquivo final para csv

aih_jornada.to_csv('..\Dados\_aih_jornada.csv', index = True, sep =';')


#Estatísticas do número de internações do paciente. A média de internações é próxima de 1 para o período considerado, com um desvio padrão de 1,5. Mais de 75% das
#observações

paciente_flat.describe()


# In[236]:


# O boxplot explicita a percepção de que não há muitos pacientes com várias internações. Isso indica que também 
# não há muita movimentação de pacientes entre hospitais. Talvez seja necessário agregar outras bases de dados para que 
# a análise da "Jornada do Paciente' seja mais significativa.
boxplot = plt.figure()
axes1 = boxplot.add_subplot(1,1,1)
axes1.boxplot(paciente_flat)
axes1.set_xlabel('Paciente')
axes1.set_ylabel('nº de internações')
axes1.set_title('Boxplot Pacientes x Internações')


# In[239]:


#fazendo gráficos para visualizar as quantidades de internações por hospital e cidade

count, ax = plt.subplots()

ax = sns.countplot('no_municipio', data = aih_jornada)
ax.set_title('Número de internações por município')
ax.set_xlabel('Município')


# In[243]:


count, ax = plt.subplots()
ax = sns.countplot(y = 'no_fantasia', data = aih_jornada)
ax.set_title('Número de internações por hospital')
ax.set_ylabel('Hospital')



