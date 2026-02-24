from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import secrets
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Simple auth
security = HTTPBasic()
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Define Models
class BlogPost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    excerpt: str
    content: str
    image_url: str
    category: str
    author: str = "Equipe Chronos"
    read_time: str = "5 min"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published: bool = True

class BlogPostCreate(BaseModel):
    title: str
    slug: str
    excerpt: str
    content: str
    image_url: str
    category: str
    author: str = "Equipe Chronos"
    read_time: str = "5 min"
    published: bool = True

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    read_time: Optional[str] = None
    published: Optional[bool] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str

# Seed data
SEED_BLOG_POSTS = [
    {
        "title": "O que é Pesquisa Clínica e Por Que Ela é Importante?",
        "slug": "o-que-e-pesquisa-clinica",
        "excerpt": "Descubra como a pesquisa clínica contribui para o avanço da medicina e o desenvolvimento de novos tratamentos que podem salvar vidas.",
        "content": """<h2>Entendendo a Pesquisa Clínica</h2>
<p>A pesquisa clínica é um processo científico rigoroso que avalia a segurança e eficácia de novos medicamentos, tratamentos e procedimentos médicos em seres humanos. Este processo é fundamental para o avanço da medicina e o desenvolvimento de terapias inovadoras.</p>

<h3>O Processo da Pesquisa Clínica</h3>
<p>Todo estudo clínico passa por fases bem definidas:</p>
<ul>
<li><strong>Fase I:</strong> Avaliação inicial de segurança em um pequeno grupo de voluntários</li>
<li><strong>Fase II:</strong> Estudo da eficácia e efeitos colaterais em um grupo maior</li>
<li><strong>Fase III:</strong> Comparação com tratamentos existentes em larga escala</li>
<li><strong>Fase IV:</strong> Monitoramento após a aprovação do medicamento</li>
</ul>

<h3>Importância para a Sociedade</h3>
<p>Todos os medicamentos que utilizamos hoje passaram por pesquisas clínicas. Sem esse processo, não teríamos acesso a tratamentos para diabetes, câncer, doenças cardíacas e muitas outras condições.</p>

<h3>Segurança e Ética</h3>
<p>A pesquisa clínica é regulamentada por órgãos como a ANVISA e comitês de ética, garantindo que os participantes estejam sempre protegidos e bem informados sobre os estudos.</p>

<p>Na Chronos Pesquisa Clínica, seguimos os mais altos padrões éticos e científicos, proporcionando aos participantes acesso a tratamentos inovadores com total segurança.</p>""",
        "image_url": "https://images.pexels.com/photos/3825586/pexels-photo-3825586.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "Educação",
        "read_time": "6 min"
    },
    {
        "title": "Como Participar de um Estudo Clínico: Guia Completo",
        "slug": "como-participar-estudo-clinico",
        "excerpt": "Um guia detalhado sobre como você pode se tornar um participante de pesquisa clínica e contribuir para o avanço da medicina.",
        "content": """<h2>Seu Caminho para Participar de Estudos Clínicos</h2>
<p>Participar de um estudo clínico é uma decisão importante que pode beneficiar não apenas você, mas também milhares de pessoas no futuro. Aqui está tudo o que você precisa saber.</p>

<h3>Passo 1: Encontre um Estudo Adequado</h3>
<p>O primeiro passo é encontrar um estudo que seja relevante para sua condição de saúde. Na Chronos, mantemos uma lista atualizada de estudos em andamento para diversas condições.</p>

<h3>Passo 2: Triagem Inicial</h3>
<p>Após entrar em contato, nossa equipe realizará uma avaliação inicial para verificar se você atende aos critérios do estudo. Isso inclui:</p>
<ul>
<li>Idade e histórico médico</li>
<li>Condição de saúde atual</li>
<li>Medicamentos em uso</li>
<li>Disponibilidade para consultas</li>
</ul>

<h3>Passo 3: Consentimento Informado</h3>
<p>Antes de participar, você receberá informações detalhadas sobre o estudo, incluindo possíveis riscos e benefícios. A participação é sempre voluntária.</p>

<h3>Passo 4: Acompanhamento</h3>
<p>Durante o estudo, você terá acompanhamento médico regular e gratuito, com acesso a exames e consultas especializadas.</p>

<h3>Seus Direitos como Participante</h3>
<p>Você pode desistir a qualquer momento, sem precisar justificar. Sua privacidade é protegida e todas as informações são confidenciais.</p>""",
        "image_url": "https://images.pexels.com/photos/4226119/pexels-photo-4226119.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "Guia",
        "read_time": "7 min"
    },
    {
        "title": "Benefícios da Pesquisa Clínica para Pacientes",
        "slug": "beneficios-pesquisa-clinica-pacientes",
        "excerpt": "Conheça as vantagens exclusivas que os participantes de estudos clínicos podem ter, desde acesso a novos tratamentos até acompanhamento especializado.",
        "content": """<h2>Por Que Participar de uma Pesquisa Clínica?</h2>
<p>A participação em pesquisas clínicas oferece uma série de benefícios importantes para os pacientes, especialmente aqueles que buscam novas opções de tratamento.</p>

<h3>Acesso a Tratamentos Inovadores</h3>
<p>Participantes têm acesso a medicamentos e terapias que ainda não estão disponíveis no mercado. Para muitos pacientes, isso representa uma esperança quando os tratamentos convencionais não funcionaram.</p>

<h3>Acompanhamento Médico Especializado</h3>
<p>Durante o estudo, você receberá:</p>
<ul>
<li>Consultas regulares com especialistas</li>
<li>Exames laboratoriais e de imagem</li>
<li>Monitoramento constante da sua saúde</li>
<li>Acesso a uma equipe multidisciplinar</li>
</ul>

<h3>Custo Zero</h3>
<p>Toda a participação no estudo é gratuita, incluindo medicamentos, exames e consultas. Em alguns casos, também há auxílio para transporte.</p>

<h3>Contribuição para a Ciência</h3>
<p>Ao participar, você contribui para o desenvolvimento de tratamentos que podem ajudar milhões de pessoas no futuro.</p>

<h3>Conhecimento Sobre Sua Condição</h3>
<p>O acompanhamento detalhado permite que você entenda melhor sua condição de saúde e aprenda a gerenciá-la de forma mais eficaz.</p>""",
        "image_url": "https://images.pexels.com/photos/5215024/pexels-photo-5215024.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "Benefícios",
        "read_time": "5 min"
    },
    {
        "title": "Quem Pode Participar de Pesquisas Clínicas?",
        "slug": "quem-pode-participar-pesquisas-clinicas",
        "excerpt": "Entenda os critérios de elegibilidade para participação em estudos clínicos e descubra se você pode ser um candidato.",
        "content": """<h2>Critérios de Elegibilidade em Pesquisas Clínicas</h2>
<p>Cada estudo clínico possui critérios específicos de inclusão e exclusão. Entender esses critérios ajuda você a identificar estudos adequados para sua situação.</p>

<h3>Critérios Comuns de Inclusão</h3>
<p>Geralmente, os estudos buscam participantes que:</p>
<ul>
<li>Tenham uma condição de saúde específica relacionada ao estudo</li>
<li>Estejam dentro de uma faixa etária determinada</li>
<li>Não estejam participando de outros estudos simultaneamente</li>
<li>Tenham disponibilidade para comparecer às visitas programadas</li>
</ul>

<h3>Critérios de Exclusão</h3>
<p>Algumas condições podem impedir a participação:</p>
<ul>
<li>Gravidez ou amamentação (em alguns estudos)</li>
<li>Uso de determinados medicamentos</li>
<li>Presença de outras condições de saúde graves</li>
<li>Histórico de reações alérgicas a componentes do estudo</li>
</ul>

<h3>Processo de Avaliação</h3>
<p>Mesmo que você não atenda a todos os critérios de um estudo, pode ser elegível para outros. Nossa equipe está preparada para avaliar seu perfil e encontrar a melhor opção.</p>

<h3>Não Desista!</h3>
<p>Se você não foi selecionado para um estudo, não desanime. Novos estudos surgem constantemente e você pode ser elegível para pesquisas futuras.</p>""",
        "image_url": "https://images.pexels.com/photos/5726706/pexels-photo-5726706.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "Informação",
        "read_time": "5 min"
    },
    {
        "title": "Pesquisa Clínica é Segura? Mitos e Verdades",
        "slug": "pesquisa-clinica-segura-mitos-verdades",
        "excerpt": "Desmistificando os principais mitos sobre pesquisa clínica e apresentando os fatos que garantem a segurança dos participantes.",
        "content": """<h2>A Verdade Sobre a Segurança em Pesquisas Clínicas</h2>
<p>É natural ter dúvidas sobre a segurança de participar de uma pesquisa clínica. Vamos esclarecer os principais mitos e apresentar os fatos.</p>

<h3>Mito 1: "Serei cobaia de laboratório"</h3>
<p><strong>Verdade:</strong> Antes de chegar aos estudos em humanos, todo tratamento passa por anos de pesquisa em laboratório. Os participantes são pacientes que recebem cuidado médico de alta qualidade.</p>

<h3>Mito 2: "Posso receber placebo sem tratamento"</h3>
<p><strong>Verdade:</strong> Estudos com placebo são raros quando já existe tratamento disponível. Quando utilizados, os participantes são informados previamente.</p>

<h3>Mito 3: "Não posso desistir depois de começar"</h3>
<p><strong>Verdade:</strong> A participação é 100% voluntária. Você pode desistir a qualquer momento, sem precisar justificar e sem prejudicar seu tratamento.</p>

<h3>Garantias de Segurança</h3>
<p>Todos os estudos são aprovados por:</p>
<ul>
<li>Comitês de Ética em Pesquisa (CEP)</li>
<li>Comissão Nacional de Ética em Pesquisa (CONEP)</li>
<li>Agência Nacional de Vigilância Sanitária (ANVISA)</li>
</ul>

<h3>Monitoramento Contínuo</h3>
<p>Durante todo o estudo, sua saúde é monitorada por profissionais qualificados. Qualquer efeito adverso é tratado imediatamente e reportado aos órgãos reguladores.</p>""",
        "image_url": "https://images.pexels.com/photos/4226769/pexels-photo-4226769.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "Segurança",
        "read_time": "6 min"
    },
    {
        "title": "Novos Tratamentos: Como Funcionam os Medicamentos Experimentais",
        "slug": "novos-tratamentos-medicamentos-experimentais",
        "excerpt": "Entenda o processo de desenvolvimento de novos medicamentos e como eles chegam até os pacientes através das pesquisas clínicas.",
        "content": """<h2>O Caminho de um Novo Medicamento</h2>
<p>Do laboratório até a farmácia, um novo medicamento percorre um longo caminho. Entender esse processo ajuda a compreender a importância das pesquisas clínicas.</p>

<h3>Descoberta e Desenvolvimento Inicial</h3>
<p>O processo começa em laboratórios de pesquisa, onde cientistas identificam moléculas promissoras. Esta fase pode levar anos de estudo e milhões em investimento.</p>

<h3>Testes Pré-Clínicos</h3>
<p>Antes de testar em humanos, o medicamento passa por extensivos testes em laboratório e modelos computacionais para avaliar sua segurança inicial.</p>

<h3>Fases dos Estudos Clínicos</h3>
<p><strong>Fase I:</strong> Pequeno grupo de voluntários saudáveis - avalia segurança</p>
<p><strong>Fase II:</strong> Grupo maior de pacientes - avalia eficácia e dosagem</p>
<p><strong>Fase III:</strong> Estudos amplos - confirma eficácia e monitora efeitos</p>
<p><strong>Fase IV:</strong> Após aprovação - monitora uso na população geral</p>

<h3>Aprovação Regulatória</h3>
<p>Após completar todas as fases, os resultados são analisados pela ANVISA, que decide se o medicamento pode ser comercializado no Brasil.</p>

<h3>Inovações em Desenvolvimento</h3>
<p>Atualmente, há pesquisas promissoras em:</p>
<ul>
<li>Terapias genéticas</li>
<li>Imunoterapias para câncer</li>
<li>Tratamentos personalizados</li>
<li>Medicamentos biológicos</li>
</ul>

<p>Na Chronos, você pode ter acesso a essas inovações antes mesmo de chegarem ao mercado.</p>""",
        "image_url": "https://images.pexels.com/photos/3825572/pexels-photo-3825572.jpeg?auto=compress&cs=tinysrgb&w=800",
        "category": "Inovação",
        "read_time": "7 min"
    }
]

@app.on_event("startup")
async def seed_database():
    count = await db.blog_posts.count_documents({})
    if count == 0:
        for post_data in SEED_BLOG_POSTS:
            post = BlogPost(**post_data)
            doc = post.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.blog_posts.insert_one(doc)
        logging.info("Seeded blog posts successfully")

# Public Routes
@api_router.get("/")
async def root():
    return {"message": "Chronos Pesquisa Clínica API"}

@api_router.get("/blog", response_model=List[BlogPost])
async def get_blog_posts():
    posts = await db.blog_posts.find({"published": True}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for post in posts:
        if isinstance(post.get('created_at'), str):
            post['created_at'] = datetime.fromisoformat(post['created_at'])
    return posts

@api_router.get("/blog/{slug}")
async def get_blog_post(slug: str):
    post = await db.blog_posts.find_one({"slug": slug, "published": True}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    if isinstance(post.get('created_at'), str):
        post['created_at'] = datetime.fromisoformat(post['created_at'])
    return post

# Auth Route
@api_router.post("/admin/login", response_model=LoginResponse)
async def admin_login(request: LoginRequest):
    if request.username == ADMIN_USERNAME and request.password == ADMIN_PASSWORD:
        return LoginResponse(success=True, message="Login realizado com sucesso")
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

# Admin Routes (Protected)
@api_router.get("/admin/posts", response_model=List[BlogPost])
async def get_all_posts(username: str = Depends(verify_admin)):
    posts = await db.blog_posts.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for post in posts:
        if isinstance(post.get('created_at'), str):
            post['created_at'] = datetime.fromisoformat(post['created_at'])
    return posts

@api_router.get("/admin/posts/{post_id}")
async def get_post_by_id(post_id: str, username: str = Depends(verify_admin)):
    post = await db.blog_posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    if isinstance(post.get('created_at'), str):
        post['created_at'] = datetime.fromisoformat(post['created_at'])
    return post

@api_router.post("/admin/posts", response_model=BlogPost)
async def create_post(input: BlogPostCreate, username: str = Depends(verify_admin)):
    # Check if slug exists
    existing = await db.blog_posts.find_one({"slug": input.slug})
    if existing:
        raise HTTPException(status_code=400, detail="Slug já existe")
    
    post = BlogPost(**input.model_dump())
    doc = post.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.blog_posts.insert_one(doc)
    return post

@api_router.put("/admin/posts/{post_id}", response_model=BlogPost)
async def update_post(post_id: str, input: BlogPostUpdate, username: str = Depends(verify_admin)):
    existing = await db.blog_posts.find_one({"id": post_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    
    update_data = {k: v for k, v in input.model_dump().items() if v is not None}
    
    if update_data:
        await db.blog_posts.update_one({"id": post_id}, {"$set": update_data})
    
    updated = await db.blog_posts.find_one({"id": post_id}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return updated

@api_router.delete("/admin/posts/{post_id}")
async def delete_post(post_id: str, username: str = Depends(verify_admin)):
    result = await db.blog_posts.delete_one({"id": post_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post não encontrado")
    return {"message": "Post excluído com sucesso"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
