import os
import sys
import pygame

pygame.init()

# 1. Tamanho real da tela (tela cheia no Android)
info = pygame.display.Info()
LARGURA, ALTURA = info.current_w, info.current_h

if LARGURA <= 0 or ALTURA <= 0:
    LARGURA, ALTURA = 800, 480
    tela = pygame.display.set_mode((LARGURA, ALTURA))
else:
    tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)

pygame.display.set_caption("Pong Quadra")
relogio = pygame.time.Clock()

tamanho_fonte = max(20, min(LARGURA, ALTURA) // 16)
fonte = pygame.font.SysFont("Arial", tamanho_fonte, bold=True)
fonte_titulo = pygame.font.SysFont("Arial", max(26, min(LARGURA, ALTURA) // 11), bold=True)
fonte_sub = pygame.font.SysFont("Arial", max(15, min(LARGURA, ALTURA) // 24), bold=False)

pasta_script = os.path.dirname(os.path.abspath(__file__))


def carregar_imagem_ajustada(nome_arquivo):
    candidatos_pasta = [
        pasta_script,
        os.getcwd(),
        "/sdcard/Download",
        "/storage/emulated/0/Download",
        "/sdcard/Pictures",
        "/storage/emulated/0/Pictures",
    ]

    variacoes_nome = [
        nome_arquivo,
        nome_arquivo.lower(),
        nome_arquivo.upper(),
        nome_arquivo.replace(".jpg", ".jpeg"),
        nome_arquivo.replace(".jpg", ".JPG"),
    ]

    caminho_encontrado = None
    for pasta in candidatos_pasta:
        if not pasta or not os.path.isdir(pasta):
            continue
        for nome in variacoes_nome:
            tentativa = os.path.join(pasta, nome)
            if os.path.exists(tentativa):
                caminho_encontrado = tentativa
                break
        if caminho_encontrado:
            break

    if not caminho_encontrado:
        return None, None

    img_original = pygame.image.load(caminho_encontrado).convert()
    orig_w, orig_h = img_original.get_size()

    # Ajusta o tamanho mantendo a proporcao original da foto
    max_w = int(LARGURA * 0.85)
    max_h = int(ALTURA * 0.50)
    escala = min(max_w / orig_w, max_h / orig_h)

    novo_w = max(1, int(orig_w * escala))
    novo_h = max(1, int(orig_h * escala))
    img_escalada = pygame.transform.smoothscale(img_original, (novo_w, novo_h))
    retangulo = img_escalada.get_rect(center=(LARGURA // 2, int(ALTURA * 0.56)))
    return img_escalada, retangulo


# 2. Carrega imagens de Game Over e You Win
imagem_game_over, ret_game_over = carregar_imagem_ajustada("155166.jpg")
imagem_you_win, ret_you_win = carregar_imagem_ajustada("155163.jpg")

# 3. Dimensoes da "Quadra" (moldura)
margem_x = max(16, LARGURA // 35)
margem_y = max(20, ALTURA // 18)
espessura_linha = max(3, min(LARGURA, ALTURA) // 140)

quadra_topo = margem_y + espessura_linha
quadra_fundo = ALTURA - margem_y - espessura_linha
quadra_direita = LARGURA - margem_x - espessura_linha

# 4. Raquete, bola, velocidade e placar
raquete_largura = max(16, LARGURA // 45)
raquete_altura = max(80, ALTURA // 5)
raquete = pygame.Rect(
    margem_x + max(24, LARGURA // 28),
    (quadra_topo + quadra_fundo) // 2 - raquete_altura // 2,
    raquete_largura,
    raquete_altura,
)

tamanho_bola = max(18, min(LARGURA, ALTURA) // 28)
bola = pygame.Rect(
    LARGURA // 2 - tamanho_bola // 2,
    (quadra_topo + quadra_fundo) // 2 - tamanho_bola // 2,
    tamanho_bola,
    tamanho_bola,
)

vel_x_base = max(4.0, LARGURA / 140.0)
vel_y_base = max(4.0, ALTURA / 110.0)
vel_x = vel_x_base
vel_y = vel_y_base

VEL_X_MAX = vel_x_base * 2.2
VEL_Y_MAX = vel_y_base * 2.2

pontos = 0
ultimo_nivel_velocidade = 0
ultimo_marco_vitoria = 0
game_over = False
tela_vitoria = False
dedo_ativo = False


def mover_raquete_para_y(novo_y):
    raquete.centery = int(novo_y)
    if raquete.top < quadra_topo:
        raquete.top = quadra_topo
    if raquete.bottom > quadra_fundo:
        raquete.bottom = quadra_fundo


def aplicar_aceleracao_por_pontos():
    global vel_x, vel_y, ultimo_nivel_velocidade

    nivel_atual = pontos // 10
    if nivel_atual > ultimo_nivel_velocidade:
        ultimo_nivel_velocidade = nivel_atual
        fator = 1.12
        dir_x = 1 if vel_x >= 0 else -1
        dir_y = 1 if vel_y >= 0 else -1

        nova_vel_x = min(abs(vel_x) * fator, VEL_X_MAX)
        nova_vel_y = min(abs(vel_y) * fator, VEL_Y_MAX)

        vel_x = nova_vel_x * dir_x
        vel_y = nova_vel_y * dir_y


def verificar_vitoria_100_pontos():
    global ultimo_marco_vitoria, tela_vitoria

    marco_atual = pontos // 100
    if marco_atual > ultimo_marco_vitoria:
        ultimo_marco_vitoria = marco_atual
        tela_vitoria = True


def reiniciar_partida():
    global vel_x, vel_y, pontos, ultimo_nivel_velocidade, ultimo_marco_vitoria, game_over, tela_vitoria

    bola.center = (LARGURA // 2, (quadra_topo + quadra_fundo) // 2)
    raquete.centery = (quadra_topo + quadra_fundo) // 2
    vel_x = abs(vel_x_base)
    vel_y = abs(vel_y_base) if vel_y >= 0 else -abs(vel_y_base)
    pontos = 0
    ultimo_nivel_velocidade = 0
    ultimo_marco_vitoria = 0
    game_over = False
    tela_vitoria = False


def desenhar_quadra_e_jogo():
    tela.fill((14, 48, 30))

    # Linha central tracejada
    centro_x = LARGURA // 2
    y_linha = quadra_topo + 8
    while y_linha < quadra_fundo - 8:
        pygame.draw.line(
            tela,
            (180, 220, 195),
            (centro_x, y_linha),
            (centro_x, min(y_linha + 14, quadra_fundo - 8)),
            max(2, espessura_linha // 2),
        )
        y_linha += 28

    # Moldura da quadra (topo, fundo e direita; esquerda aberta para defesa)
    cor_linha = (240, 245, 240)
    pygame.draw.line(tela, cor_linha, (margem_x, margem_y), (quadra_direita, margem_y), espessura_linha)
    pygame.draw.line(
        tela,
        cor_linha,
        (margem_x, ALTURA - margem_y),
        (quadra_direita, ALTURA - margem_y),
        espessura_linha,
    )
    pygame.draw.line(
        tela,
        cor_linha,
        (quadra_direita, margem_y),
        (quadra_direita, ALTURA - margem_y),
        espessura_linha,
    )

    pygame.draw.rect(tela, (255, 255, 255), raquete, border_radius=4)
    pygame.draw.ellipse(tela, (255, 235, 90), bola)

    texto_pontos = fonte.render(f"Pontos: {pontos}", True, (255, 255, 255))
    tela.blit(
        texto_pontos,
        (LARGURA // 2 - texto_pontos.get_width() // 2, quadra_topo + max(8, ALTURA // 50)),
    )


# 5. Loop principal do jogo
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.FINGERDOWN:
            if game_over:
                reiniciar_partida()
            elif tela_vitoria:
                tela_vitoria = False
                dedo_ativo = False
            else:
                dedo_ativo = True
                mover_raquete_para_y(evento.y * ALTURA)

        elif evento.type == pygame.FINGERMOTION:
            if not game_over and not tela_vitoria:
                mover_raquete_para_y(evento.y * ALTURA)

        elif evento.type == pygame.FINGERUP:
            dedo_ativo = False

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                reiniciar_partida()
            elif tela_vitoria:
                tela_vitoria = False
                dedo_ativo = False
            else:
                dedo_ativo = True
                mover_raquete_para_y(evento.pos[1])

        elif evento.type == pygame.MOUSEMOTION and evento.buttons[0]:
            if not game_over and not tela_vitoria:
                mover_raquete_para_y(evento.pos[1])

        elif evento.type == pygame.MOUSEBUTTONUP:
            dedo_ativo = False

    if not game_over and not tela_vitoria:
        # Move a bola
        bola.x += int(round(vel_x))
        bola.y += int(round(vel_y))

        # Bate no teto ou no chao da quadra
        if bola.top <= quadra_topo:
            bola.top = quadra_topo
            vel_y *= -1
        elif bola.bottom >= quadra_fundo:
            bola.bottom = quadra_fundo
            vel_y *= -1

        # Bate na parede direita da quadra
        if bola.right >= quadra_direita:
            bola.right = quadra_direita
            vel_x *= -1

        # Bate na raquete (lado esquerdo)
        if bola.colliderect(raquete) and vel_x < 0:
            bola.left = raquete.right
            vel_x *= -1
            pontos = pontos + 1
            aplicar_aceleracao_por_pontos()
            verificar_vitoria_100_pontos()

        # Se passar da borda esquerda, ativa tela de Game Over
        if bola.left <= margem_x:
            game_over = True

        desenhar_quadra_e_jogo()

    elif tela_vitoria:
        tela.fill((25, 22, 14))

        titulo_win = fonte_titulo.render("YOU WIN!", True, (255, 215, 60))
        tela.blit(titulo_win, (LARGURA // 2 - titulo_win.get_width() // 2, max(20, ALTURA // 16)))

        texto_marco = fonte.render(f"Marco alcançado: {pontos} pontos", True, (255, 255, 255))
        tela.blit(
            texto_marco,
            (LARGURA // 2 - texto_marco.get_width() // 2, max(75, ALTURA // 6)),
        )

        if imagem_you_win is not None and ret_you_win is not None:
            tela.blit(imagem_you_win, ret_you_win)
        else:
            aviso_win = fonte_sub.render("Imagem 155163.jpg não encontrada na pasta", True, (220, 220, 220))
            tela.blit(aviso_win, (LARGURA // 2 - aviso_win.get_width() // 2, ALTURA // 2))

        texto_continuar = fonte_sub.render("Toque na tela para continuar jogando", True, (180, 235, 195))
        tela.blit(
            texto_continuar,
            (LARGURA // 2 - texto_continuar.get_width() // 2, ALTURA - max(45, ALTURA // 12)),
        )

    else:
        tela.fill((0, 0, 0))

        titulo_go = fonte_titulo.render("GAME OVER", True, (255, 80, 80))
        tela.blit(titulo_go, (LARGURA // 2 - titulo_go.get_width() // 2, max(20, ALTURA // 16)))

        texto_final = fonte.render(f"Pontuação final: {pontos}", True, (255, 255, 255))
        tela.blit(
            texto_final,
            (LARGURA // 2 - texto_final.get_width() // 2, max(75, ALTURA // 6)),
        )

        if imagem_game_over is not None and ret_game_over is not None:
            tela.blit(imagem_game_over, ret_game_over)
        else:
            aviso_img = fonte_sub.render("Imagem 155166.jpg não encontrada na pasta", True, (200, 200, 200))
            tela.blit(aviso_img, (LARGURA // 2 - aviso_img.get_width() // 2, ALTURA // 2))

        texto_reiniciar = fonte_sub.render("Toque na tela para jogar novamente", True, (180, 230, 190))
        tela.blit(
            texto_reiniciar,
            (LARGURA // 2 - texto_reiniciar.get_width() // 2, ALTURA - max(45, ALTURA // 12)),
        )

    pygame.display.flip()
    relogio.tick(60)
