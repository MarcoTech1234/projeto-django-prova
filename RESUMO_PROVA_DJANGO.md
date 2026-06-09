# 📚 RESUMO DJANGO PARA PROVA - 5º SEMESTRE ADS

## 🎯 O PROJETO: Agenda de Contatos (Contact Management System)
Um aplicativo web para gerenciar contatos pessoais com funcionalidades de CRUD, busca, categorização e upload de fotos.

---

## 1️⃣ CONCEITOS FUNDAMENTAIS DO DJANGO

### O que é Django?
- **Framework web Python** de alto nível
- Segue padrão **MTV (Model-Template-View)**
  - **Model**: Camada de dados (banco de dados)
  - **Template**: Camada de apresentação (HTML)
  - **View**: Lógica da aplicação (processamento)
- É um **ORM (Object-Relational Mapping)** - mapeia tabelas do BD como classes Python

### Estrutura do Projeto Django
```
projeto/
├── manage.py          # Comando para gerenciar o projeto
├── project/           # Pasta de configuração do projeto
│   ├── settings.py    # Configurações gerais
│   ├── urls.py        # Roteamento de URLs
│   ├── wsgi.py        # Servidor web
│   └── asgi.py        # Servidor assíncrono
├── contact/           # Aplicação (app) específica
│   ├── models.py      # Modelos de dados
│   ├── views.py       # Lógica das views
│   ├── forms.py       # Formulários
│   ├── urls.py        # URLs da app
│   ├── admin.py       # Admin customizado
│   └── migrations/    # Histórico de mudanças no BD
├── requirements.txt   # Dependências Python
└── db.sqlite3        # Banco de dados
```

---

## 2️⃣ MODELS (Modelos de Dados)

### O que são Models?
- Classes Python que representam **tabelas do banco de dados**
- Cada atributo é um **campo (coluna) da tabela**
- Django cria as tabelas automaticamente

### Models do Projeto

#### **Model: Contact (Contato)**
```python
class Contact(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    show = models.BooleanField(default=True)
    picture = models.ImageField(blank=True, upload_to="pictures/%Y/%m/")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
```

**Tipos de Campos:**
- `CharField`: Texto curto (até max_length caracteres)
- `TextField`: Texto longo (sem limite)
- `EmailField`: Email validado
- `ImageField`: Upload de imagens
- `BooleanField`: Verdadeiro/Falso
- `DateTimeField`: Data e hora
- `ForeignKey`: Relacionamento com outra tabela (1:N)

**Parâmetros Importantes:**
- `max_length`: Tamanho máximo
- `blank=True`: Campo opcional no formulário
- `null=True`: Permite valores nulos no BD
- `default`: Valor padrão
- `upload_to`: Pasta para armazenar arquivos

#### **Model: Category (Categoria)**
```python
class Category(models.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
    
    def __str__(self):
        return self.name
```

**Class Meta:**
- Define configurações e metadados do modelo
- `verbose_name`: Nome singular em português
- `verbose_name_plural`: Nome plural em português

### Relacionamentos
```python
# ForeignKey = Relacionamento 1:N (Um para Muitos)
category = models.ForeignKey(Category, on_delete=models.SET_NULL, ...)

# Opções de on_delete:
# - models.CASCADE: Deleta o contato se a categoria for deletada
# - models.SET_NULL: Coloca NULL no contato
# - models.PROTECT: Impede deletar se houver contatos
```

### Migrações
```bash
# Detectar mudanças nos models
python manage.py makemigrations

# Aplicar as mudanças no BD
python manage.py migrate
```

---

## 3️⃣ VIEWS (Lógica da Aplicação)

### O que é uma View?
- Função ou classe que **processa requisições HTTP**
- Retorna uma resposta (HTML, JSON, redirect, etc.)
- Recebe a requisição do usuário, processa e devolve

### Views do Projeto

#### **1. INDEX - Listar todos os contatos**
```python
def index(request):
    # Filtra apenas contatos com show=True
    contacts = Contact.objects.filter(show=True).order_by('-id')
    
    # Paginação (15 contatos por página)
    paginator = Paginator(contacts, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'contact/index.html', context)
```

**Conceitos:**
- `Contact.objects.all()`: Busca todos os contatos
- `filter(show=True)`: Filtra apenas visíveis
- `order_by('-id')`: Ordena por ID (descendente com -)
- `Paginator`: Divide resultados em páginas
- `render()`: Renderiza template com contexto

#### **2. CONTACT - Ver detalhes de um contato**
```python
def contact(request, contact_id):
    single_contact = Contact.objects.get(pk=contact_id)
    
    context = {
        'contact': single_contact,
        'site_title': f'{single_contact.first_name} {single_contact.last_name} - '
    }
    
    return render(request, 'contact/contact.html', context)
```

**Conceitos:**
- `pk` = primary key (ID)
- `.get()`: Retorna um objeto ou erro se não encontrar
- `.first()`: Retorna o primeiro ou None se não encontrar

#### **3. SEARCH - Buscar contatos**
```python
def search(request):
    search_value = request.GET.get('q', '').strip()
    
    if search_value == '':
        return redirect('contact:index')
    
    # Q = Query Object para usar OR nas buscas
    contacts = Contact.objects \
        .filter(show=True) \
        .filter(
            Q(first_name__icontains=search_value) |  # OU
            Q(last_name__icontains=search_value) |
            Q(email__icontains=search_value)
        ) \
        .order_by('-id')
    
    paginator = Paginator(contacts, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    
    context = {'page_obj': page_obj, 'site_title': 'Search - '}
    return render(request, 'contact/index.html', context)
```

**Buscas no Django:**
- `__icontains`: Busca case-insensitive
- `__contains`: Busca case-sensitive
- `__startswith`: Começa com
- `__endswith`: Termina com
- `Q()`: Permite OR (|) e AND (&) nas buscas

#### **4. CREATE - Criar novo contato**
```python
def create(request):
    form_action = reverse('contact:create')
    
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        
        if form.is_valid():
            contact = form.save()  # Salva no BD
            return redirect('contact:update', contact_id=contact.pk)
        
        # Redisplaya o formulário com erros
        return render(request, 'contact/create.html', {'form': form, ...})
    
    # GET: Mostra formulário vazio
    return render(request, 'contact/create.html', 
                 {'form': ContactForm()})
```

**Conceitos:**
- `request.method == 'POST'`: Diferencia GET (carregar form) de POST (enviar dados)
- `request.FILES`: Arquivo enviado
- `form.is_valid()`: Valida dados do formulário
- `form.save()`: Salva no banco de dados
- `reverse()`: Gera URL pela rota nomeada

#### **5. UPDATE - Editar contato**
```python
def update(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id, show=True)
    
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)
        
        if form.is_valid():
            contact = form.save()
            return redirect('contact:update', contact_id=contact.pk)
    
    # GET: Mostra formulário preenchido
    form = ContactForm(instance=contact)
    return render(request, 'contact/create.html', {'form': form, ...})
```

**Conceitos:**
- `instance=contact`: Preenche o formulário com dados existentes
- `get_object_or_404()`: Retorna 404 se não encontrar

#### **6. DELETE - Deletar contato**
```python
def delete(request, contact_id):
    contact = get_object_or_404(Contact, pk=contact_id, show=True)
    
    confirmation = request.POST.get('confirmation', 'no')
    
    if confirmation == 'yes':
        contact.delete()
        return redirect('contact:index')
    
    return render(request, 'contact/contact.html', {
        'contact': contact,
        'confirmation': confirmation
    })
```

### Padrão CRUD (Create, Read, Update, Delete)
```
CREATE = Criar novo registro (POST)
READ   = Ler/listar registros (GET)
UPDATE = Editar registro (POST)
DELETE = Deletar registro (POST/DELETE)
```

---

## 4️⃣ FORMS (Formulários)

### O que é um Formulário Django?
- Classe que define campos de um formulário HTML
- Valida dados do usuário
- `ModelForm`: Formulário baseado em um Model

### Form do Projeto

```python
class ContactForm(forms.ModelForm):
    picture = forms.ImageField(
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'classe-a classe-b',
            'placeholder': 'Aqui veio do init',
        }),
        label='Primeiro Nome',
        help_text='Texto de ajuda para seu usuário',
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'phone', 'email', 
                 'description', 'category', 'picture')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if first_name == last_name:
            msg = ValidationError('Primeiro nome não pode ser igual ao segundo')
            self.add_error('first_name', msg)
            self.add_error('last_name', msg)
```

**Conceitos:**
- `Meta.model`: Qual modelo usar
- `Meta.fields`: Quais campos mostrar no formulário
- `clean()`: Validação customizada
- `widget`: HTML renderizado (TextInput, FileInput, etc.)
- `attrs`: Atributos HTML (class, placeholder, etc.)
- `label`: Texto do label
- `help_text`: Ajuda para o usuário

---

## 5️⃣ URLS (Roteamento)

### URL Routing
- Define qual view executa para cada URL
- Usa padrões de URL com `path()` ou `re_path()`

### URLs do Projeto

**`contact/urls.py`:**
```python
app_name = 'contact'  # Namespace para as URLs

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('contact/<int:contact_id>/', views.contact, name='contact'),
    path('contact/create/', views.create, name='create'),
    path('contact/<int:contact_id>/update/', views.update, name='update'),
    path('contact/<int:contact_id>/delete/', views.delete, name='delete'),
]
```

**`project/urls.py`:**
```python
urlpatterns = [
    path('', include('contact.urls')),  # Inclui URLs da app
    path('admin/', admin.site.urls),
]
```

**Tipos de Parâmetros:**
- `<int:contact_id>`: Número inteiro
- `<str:slug>`: Texto
- `<uuid:uuid>`: UUID
- `<path:path>`: Caminho com /

**Uso em Templates:**
```html
<!-- Gera URL pela rota nomeada -->
<a href="{% url 'contact:index' %}">Home</a>
<a href="{% url 'contact:contact' contact.id %}">Ver Detalhes</a>
<a href="{% url 'contact:update' contact.id %}">Editar</a>
```

---

## 6️⃣ SETTINGS.PY (Configurações)

### Principais Configurações

```python
# Caminho do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Segurança
SECRET_KEY = '...'  # Chave secreta
DEBUG = True  # True = desenvolvimento, False = produção
ALLOWED_HOSTS = ['*']  # Hosts permitidos

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',      # Admin Django
    'django.contrib.auth',       # Autenticação
    'django.contrib.contenttypes',  # Content types
    'django.contrib.sessions',   # Sessões
    'django.contrib.messages',   # Mensagens
    'django.contrib.staticfiles',  # Arquivos estáticos
    'contact',  # Nossa app
]

# Middleware (processa requisições/respostas)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF Protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'base_templates'],
        'APP_DIRS': True,  # Procura em templates/ da app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos estáticos
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = (BASE_DIR / 'base_static',)

# Arquivos de media (uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media/'
```

---

## 7️⃣ ADMIN (Administração)

### Django Admin
- Painel administrativo automático
- Permite CRUD de dados sem escrever código
- Acesso em `/admin/`

### Customização

```python
@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = 'id', 'first_name', 'last_name', 'phone', 'photo', 'show'
    ordering = '-id'  # Ordena por ID descendente
    list_filter = 'created_date'  # Filtros na lateral
    search_fields = 'id', 'first_name', 'last_name'  # Busca
    list_per_page = 10  # Itens por página
    list_max_show_all = 200  # Máximo de itens sem paginação
    list_editable = 'first_name', 'last_name'  # Editar na lista
    list_display_links = 'id', 'phone'  # Links clicáveis
    readonly_fields = ('photo',)  # Campo somente leitura
    
    def photo(self, obj):
        if obj.picture:
            return format_html(
                '<img src="{}" width="80" height="80" />',
                obj.picture.url
            )
        return '-'
    
    photo.short_description = 'Foto'
```

---

## 8️⃣ QUERYSETS (Consultas ao BD)

### Métodos Principais

```python
# Buscar TODOS
Contact.objects.all()

# Buscar COM FILTRO
Contact.objects.filter(show=True)
Contact.objects.filter(show=True, category=1)

# Buscar COM MÚLTIPLOS FILTROS (AND)
Contact.objects \
    .filter(show=True) \
    .filter(category__name='Amigos')

# Buscar COM OR
from django.db.models import Q
Contact.objects.filter(
    Q(first_name='João') | Q(first_name='Maria')
)

# Buscar COM AND/OR
Contact.objects.filter(
    Q(show=True) & Q(category=1)
)

# Contar
Contact.objects.filter(show=True).count()

# Ordenar
Contact.objects.all().order_by('first_name')  # Crescente
Contact.objects.all().order_by('-id')  # Decrescente

# Limitar
Contact.objects.all()[:10]  # Primeiros 10

# Get (um resultado) vs Filter (lista)
contact = Contact.objects.get(pk=1)  # Erro se não encontrar
contact = Contact.objects.filter(pk=1).first()  # None se não encontrar

# Valores específicos
Contact.objects.values('first_name', 'last_name')

# Distinct (sem duplicatas)
Contact.objects.distinct()

# Contém
Contact.objects.filter(first_name__icontains='João')

# Starts with
Contact.objects.filter(first_name__startswith='J')

# Ends with
Contact.objects.filter(email__endswith='@gmail.com')

# In (em uma lista)
Contact.objects.filter(id__in=[1, 2, 3])

# Greater than / Less than
Contact.objects.filter(id__gt=10)
Contact.objects.filter(id__lt=100)
```

---

## 9️⃣ ORM (Object-Relational Mapping)

### O que é ORM?
- Mapeia **objetos Python** para **tabelas do BD**
- Não precisa escrever SQL puro
- Automático e seguro contra SQL Injection

### Exemplo ORM vs SQL

**SQL Puro:**
```sql
SELECT * FROM contact_contact WHERE show = 1 ORDER BY id DESC;
```

**Django ORM:**
```python
Contact.objects.filter(show=True).order_by('-id')
```

### Vantagens
✅ Código mais Python (pythônico)
✅ Segurança contra SQL Injection
✅ Compatibilidade com múltiplos BDs (SQLite, PostgreSQL, MySQL, etc.)
✅ Migrations automáticas

---

## 🔟 TEMPLATES (Templates HTML)

### Variáveis no Template
```html
<!-- Renderizar variável -->
<h1>{{ site_title }}</h1>

<!-- Acessar atributo -->
<p>{{ contact.first_name }} {{ contact.last_name }}</p>

<!-- Atributo de relacionamento -->
<p>Categoria: {{ contact.category.name }}</p>
```

### Tags de Lógica
```html
<!-- If -->
{% if contact.picture %}
    <img src="{{ contact.picture.url }}" />
{% else %}
    <p>Sem foto</p>
{% endif %}

<!-- Loop -->
{% for contact in page_obj %}
    <p>{{ contact.first_name }}</p>
{% endfor %}

<!-- URL (gera URL pela rota) -->
<a href="{% url 'contact:contact' contact.id %}">Ver</a>

<!-- Static (arquivo estático) -->
<link rel="stylesheet" href="{% static 'css/style.css' %}">

<!-- CSRF Token (segurança em POST) -->
<form method="post">
    {% csrf_token %}
    ...
</form>
```

### Filters (Filtros)
```html
{{ text|upper }}           <!-- Maiúscula -->
{{ text|lower }}           <!-- Minúscula -->
{{ text|truncatewords:10 }} <!-- Truncar -->
{{ date|date:"d/m/Y" }}    <!-- Formatar data -->
{{ price|floatformat:2 }}  <!-- Decimais -->
{{ list|length }}          <!-- Comprimento -->
```

---

## 1️⃣1️⃣ MIGRAÇÕES (Histórico do BD)

### O que é Migração?
- Arquivo Python que descreve mudanças no BD
- Histórico versionado de alterações
- Permite desfazer mudanças (`migrate --zero`)

### Fluxo de Migrações

```bash
# 1. Modificar models.py
# Exemplo: adicionar novo campo

# 2. Criar arquivo de migração
python manage.py makemigrations

# 3. Ver o SQL que será executado
python manage.py sqlmigrate contact 0005

# 4. Aplicar no BD
python manage.py migrate

# 5. Reverter migração (desfazer)
python manage.py migrate contact 0004
```

### Arquivo de Migração (Exemplo)
```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('contact', '0003_category_contact_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='picture',
            field=models.ImageField(blank=True, upload_to='pictures/%Y/%m/'),
        ),
    ]
```

---

## 1️⃣2️⃣ SEGURANÇA NO DJANGO

### CSRF (Cross-Site Request Forgery)
- Token de segurança para POST/PUT/DELETE
- Obrigatório em todos os formulários

```html
<form method="post">
    {% csrf_token %}
    ...
</form>
```

### SQL Injection
- **ORM previne automaticamente**
- ✅ Seguro: `Contact.objects.filter(name=user_input)`
- ❌ Inseguro: `Contact.objects.raw(f"SELECT * WHERE name = '{user_input}'")`

### Senhas
- Django **hash automaticamente** com bcrypt
- `User.objects.create_user(username, password=pwd)`
- Nunca salvar senha em texto plano

### Validação de Input
- Sempre validar dados do usuário
- Usar `form.is_valid()`
- Validação customizada em `clean()`

---

## 1️⃣3️⃣ PAGINAÇÃO

```python
from django.core.paginator import Paginator

def index(request):
    contacts = Contact.objects.all()
    
    paginator = Paginator(contacts, 15)  # 15 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'template.html', {'page_obj': page_obj})
```

**No Template:**
```html
{% for contact in page_obj %}
    <p>{{ contact.first_name }}</p>
{% endfor %}

<!-- Navegação de páginas -->
<div class="pagination">
    {% if page_obj.has_previous %}
        <a href="?page=1">« Primeira</a>
        <a href="?page={{ page_obj.previous_page_number }}">‹ Anterior</a>
    {% endif %}

    <span>{{ page_obj.number }} de {{ page_obj.paginator.num_pages }}</span>

    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}">Próxima ›</a>
        <a href="?page={{ page_obj.paginator.num_pages }}">Última »</a>
    {% endif %}
</div>
```

---

## 1️⃣4️⃣ COMANDOS DJANGO ÚTEIS

```bash
# Iniciar novo projeto
django-admin startproject nome_projeto

# Iniciar nova app
python manage.py startapp nome_app

# Servidor de desenvolvimento
python manage.py runserver
python manage.py runserver 0.0.0.0:8000  # Acessível na rede

# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Shell interativo (testar código)
python manage.py shell

# Criar superusuário (admin)
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Limpar BD (DELETE ALL)
python manage.py flush

# Ver migrações pendentes
python manage.py showmigrations

# Desfazer até migração específica
python manage.py migrate app_name zero
```

---

## 1️⃣5️⃣ PADRÃO MTV DO DJANGO

```
REQUISIÇÃO HTTP
    ↓
URLS.PY (roteamento) → Qual view?
    ↓
VIEW (lógica) → Buscar dados do BD?
    ↓
MODELS (ORM) → Consulta ao BD
    ↓
TEMPLATE (HTML) → Renderizar resposta
    ↓
RESPOSTA HTTP (HTML)
```

---

## 1️⃣6️⃣ DICAS E MACETES

### Debugging
```python
# Print a query SQL
print(Contact.objects.filter(show=True).query)

# Usar Django Shell
python manage.py shell
>>> from contact.models import Contact
>>> Contact.objects.all()
>>> contact = Contact.objects.first()
>>> contact.first_name
```

### Validação de Email
```python
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

# Automático em EmailField
email = models.EmailField()

# Manual
validator = EmailValidator()
try:
    validator('email@example.com')
except ValidationError:
    print("Email inválido")
```

### Timezone
```python
from django.utils import timezone

# Data/hora atual
now = timezone.now()

# No settings.py
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True
```

### Reverse URL
```python
from django.urls import reverse

# Gera URL pela rota nomeada
url = reverse('contact:contact', args=[1])
# Resultado: /contact/1/
```

### Redirect
```python
from django.shortcuts import redirect

# Redireciona para outra URL
return redirect('contact:index')
return redirect('/contact/')
```

---

## 🎓 RESUMO: O FLUXO DO PROJETO

1. **Usuário acessa `/`** → URL define que vai para `index` view
2. **View index** → Busca contatos do BD com `Contact.objects.filter(show=True)`
3. **View renderiza template** → Passa `page_obj` para o template
4. **Template exibe** → Loop `{% for contact in page_obj %}` mostra contatos

---

## ❓ POSSÍVEIS QUESTÕES DE PROVA

### Conceituais
- O que é MTV? Model-Template-View: separação de lógica, apresentação e dados
- Por que Django é seguro contra SQL Injection? Usa ORM que parameteriza queries
- Qual a diferença entre ForeignKey e ManyToMany? FK = 1:N, M2M = N:N
- Quando usar `filter()` vs `get()`? filter retorna lista, get retorna um ou erro
- O que é uma migração? Arquivo que descreve mudanças no BD

### Práticas
- **Criar um modelo:** Definir classe herdando de `models.Model` com campos
- **Criar uma view:** Função que recebe `request`, busca dados, renderiza template
- **Fazer uma consulta:** `Model.objects.filter(...).order_by(...)`
- **Criar um formulário:** Classe herdando de `forms.ModelForm` com Meta
- **Validar dados:** Usar `form.is_valid()` e método `clean()`

---

**BOA SORTE NA PROVA! 🚀**
