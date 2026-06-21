# EntelekX — Media Forge

## Goal

Enable the user to generate and refine images, video, audio, 3D assets and design artefacts without leaving EntelekX. This is the creative layer of the OS.

## Capabilities

| Media Type | Examples |
|---|---|
| Images | Hero images, product shots, social creatives, avatars |
| Video | Motion graphics, product demos, UGC-style clips |
| Audio | Voiceover, music, sound effects |
| 3D | Simple models, GLB exports |
| Design | Decks, landing page prototypes, brand systems |

## Integration Strategy

Primary integration via **Higgsfield MCP** (or direct API where appropriate):
- `generate_image` → Higgsfield GPT Image 2 / product-photoshoot
- `generate_video` → Higgsfield Seedance / Kling / Veo
- `generate_audio` → Higgsfield Mirelo / Sonilo
- `generate_3d` → Higgsfield multi-image-to-3D

Fallback and local alternatives:
- Local Stable Diffusion / ComfyUI workflows (future).
- Local TTS (Edge TTS, Piper).
- Local music generation (future).

## Workflow

1. User requests media in chat or via Dev Studio.
2. Agent decides parameters, prompt and model.
3. Media generation is dispatched (async).
4. Progress streamed to UI.
5. Result appears in chat and gallery.
6. User can iterate, remix or export to project.

## Design Handoff

- Generate `DESIGN.md` brand system.
- Generate UI prototypes in HTML/CSS/JSX.
- Export to Dev Studio project as starting point.
- Inspired by Open Design patterns.

## Gallery

- Central gallery for all generated media.
- Metadata: prompt, model, parameters, project, cost.
- Versions and iterations.

## Related

- [[08_Dev_Studio]]
- [[09_Life_OS]]
- [[50_Research/Higgsfield_Integration]]
- [[50_Research/Open_Design_Analysis]]
