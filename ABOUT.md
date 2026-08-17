# El About de GitHub

Texto para configurar el repositorio en GitHub. El repo vive en `julian-najas/whatsapp-agentkit`
(privado) y está congelado como candidato para auditoría.

## Estado actual

- Repo privado, rama `main`, con el árbol completo: `blueprint/`, `docs/`, `scripts/`,
  `plantillas/`, `contratos/`, `pruebas/`, `agents/`, `LICENSE`, `README.md`.
- No se publica todavía. No se pasa a público sin orden explícita.

## La descripción

GitHub corta el About en 350 caracteres. Ésta tiene 320:

> Repo blueprint para Claude Code: no trae la app, trae las instrucciones para construirla en tu
> máquina paso a paso. Un agente que atiende cada chat de WhatsApp como setter y closer: califica,
> responde la objeción, agenda y escribe el CRM. 16 archivos por fase, 30 versiones fijadas,
> compuerta de 23 chequeos. En español.

```bash
gh repo edit julian-najas/whatsapp-agentkit \
  --description "Repo blueprint para Claude Code: no trae la app, trae las instrucciones para construirla en tu máquina paso a paso. Un agente que atiende cada chat de WhatsApp como setter y closer: califica, responde la objeción, agenda y escribe el CRM. 16 archivos por fase, 30 versiones fijadas, compuerta de 23 chequeos. En español."
```

## Los topics

Veinte, el máximo que acepta GitHub. Todos en minúscula y con guiones:

`whatsapp`, `whatsapp-cloud-api`, `meta-cloud-api`, `whatsapp-bot`, `claude-code`, `anthropic`,
`agent`, `ai-agent`, `blueprint`, `sales`, `sales-automation`, `lead-qualification`, `crm`,
`chatbot`, `fastapi`, `python`, `railway`, `google-calendar`, `whisper`, `spanish`.

## La URL del sitio (GitHub Pages)

Se sirve desde `docs/` de la rama por defecto. La URL todavía no existe; queda como placeholder
hasta que se prenda Pages:

```
<URL_DOCS_COSAS_AGENTICAS>/
```

Prender Pages y apuntar a `/docs` queda para cuando el repo se haga público. Antes, no.
