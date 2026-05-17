Plano — 5 fases incrementais
Fase 1 — Fundações (0,5 dia)
Objetivo: estabelecer tokens, hooks e convenções antes de tocar em tela.

Estender tailwind.config.ts com breakpoints nomeados semânticos (xs: 480px, mantendo sm/md/lg/xl padrão) e garantir que todo CSS do projeto use mobile-first.
Adicionar a styles/tokens.ts um bloco breakpoints + layout.sidebar.widthMobile para coerência.
Criar hook hooks/useMediaQuery.ts e hooks/useIsMobile.ts (wrapper em md).
Criar components/layout/MobileDrawer.tsx reaproveitável (overlay + slide-in + trap focus + fechamento por ESC/backdrop).
Adicionar utilitário safe-area no index.css (env(safe-area-inset-*)) para iOS notch.
Fase 2 — Shell, Sidebar e Topbar (1 dia)
Objetivo: navegação global funcional em mobile.

Shell.tsx — trocar flex h-screen por flex flex-col md:flex-row min-h-screen. Sidebar só renderiza inline em md:; abaixo vira drawer.
Topbar.tsx — adicionar botão hamburger visível só em < md, ligado a estado no Shell (Context ou prop drill simples).
Sidebar.tsx — receber prop variant: 'inline' | 'drawer'. No drawer: largura maior (w-72), fecha ao clicar num item, backdrop escuro.
Ajustar Topbar para logo centralizada em mobile, ações (sino de notificação, avatar) à direita.
Fase 3 — Páginas de listagem e dashboard (1,5 dia)
Objetivo: conteúdo legível em 360–768px sem scroll horizontal.

DashboardPareceresPage.tsx — barra de pipeline: grid-cols-2 xs:grid-cols-4 md:grid-cols-8; cards de métrica já ok; blocos "municípios/advogados/mais antigos" passar de grid-cols-2 para grid-cols-1 md:grid-cols-2; padding de página px-4 md:px-6.
ParecerList.tsx + ParecerCard.tsx — garantir flex-wrap nos meta dados do card, esconder colunas secundárias em mobile (hidden sm:inline), status badge sempre visível.
ParecerFilters.tsx — em mobile: filtros empilhados verticalmente, com "Mais filtros" em <details> colapsável para economizar espaço.
LoginPage.tsx — revisar padding e tamanho do card (w-full max-w-sm px-4).
Fase 4 — Editor (/pareceres/:id) (2 dias — o mais pesado)
Objetivo: editor jurídico utilizável em tablet; funcional em celular.

SplitView.tsx — em < lg: toggle de abas ("Original" / "Editado") em vez de split lado-a-lado; em lg: manter w-1/2. Estado local do SplitView controla aba ativa.
EditorSidebar.tsx — virar drawer lateral (reutilizar MobileDrawer) acionado por botão na EditorToolbar.
EditorToolbar.tsx — em mobile: barra compacta com overflow-menu (…); agrupar botões em seções escondidas atrás de dropdown.
Modais (PeerReviewModal, CompletedReviewModal): usar max-w-2xl w-[95vw] max-h-[90vh]; grids internos grid-cols-1 md:grid-cols-2; padding responsivo.
index.css ProseMirror — envolver regras de impressão/página em @media (min-width: 768px); em mobile usar padding: 1rem, font-size: 16px, remover margens em cm.
Fase 5 — Kanban e DJe (1 dia)
KanbanBoard.tsx — em mobile (< md): exibir uma coluna por vez com swipe/tabs de navegação entre colunas; em md: voltar ao layout horizontal.
TaskCard.tsx / KanbanColumn.tsx — revisar densidade (p-3 md:p-4, text-sm).
TaskDetailModal.tsx e CreateTaskModal.tsx — grid-cols-1 md:grid-cols-2, largura fluida.
MovementList.tsx:68,79 — formulário para grid-cols-1 sm:grid-cols-2; botões full-width em mobile.
MovementCard.tsx + MovementDetail.tsx — metadados em flex-wrap, truncation com line-clamp.
Fase 6 — Polimento e QA (0,5 dia)
Testar em 360px (iPhone SE), 390px (iPhone 14), 768px (iPad), 1024px, 1440px.
Testar touch: alvos mínimos de 44×44px em botões e links.
Testar teclado virtual: inputs não cobertos; uso de scrollIntoView no focus se necessário.
Acessibilidade: aria-label no hamburger, role="dialog" no drawer, foco gerenciado.
Verificar orientação landscape no editor (tablets).
Lighthouse mobile score (meta ≥ 90 em Best Practices e Accessibility).
Convenções que proponho adotar
Mobile-first: classes sem prefixo = mobile; md:, lg: para telas maiores.
Padding de página: px-4 md:px-6 lg:px-8.
Grid de formulários: sempre grid-cols-1 md:grid-cols-2 por padrão.
Modais: w-[95vw] max-w-2xl max-h-[90vh] overflow-y-auto.
Drawer: tudo que é w-56+ lateral em desktop vira drawer em < md.
Proibido: w-[NNpx], h-screen sem contrapartida min-h-screen, grid-cols-N sem breakpoint de fallback.

Riscos
Editor TipTap: regras ProseMirror com unidades físicas (cm, pt) podem conflitar — recomendo separar "modo visualização" (paginado, cm) de "modo edição mobile" (fluido, rem).
Kanban em mobile exige decisão de UX (tabs vs. scroll vs. accordion) — vale validar com usuário antes de implementar.
Densidade informacional do dashboard: em telas pequenas alguns cards precisarão ser escondidos ou priorizados.