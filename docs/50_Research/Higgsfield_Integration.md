# Higgsfield Integration

## Summary

Higgsfield is an AI media generation platform. It supports image, video, audio, 3D and ad creative generation via multiple models.

## Relevant Capabilities

| Capability | Models |
|---|---|
| Image generation | GPT Image 2, Nano Banana, Marketing Studio |
| Video generation | Seedance 2.0, Kling 3.0 |
| Audio/music | Mirelo (audio), Sonilo (music) |
| 3D | Multi-image-to-3D |
| Avatar/identity | Soul Character training |
| Product/marketplace | Product-photoshoot, marketplace cards |

## Integration Strategy for EntelekX

- Primary: **MCP server** exposing Higgsfield tools.
- Secondary: direct API calls where MCP is insufficient.
- Lazy dependency installation to avoid bloating core install.

## Tools to Expose

- `generate_image`
- `generate_video`
- `generate_audio`
- `generate_music`
- `generate_3d`
- `generate_marketplace_card`
- `train_soul_character` (future)

## Workflow

1. User requests media in chat.
2. Agent selects appropriate Higgsfield tool/model.
3. Async generation with progress streaming.
4. Result stored in gallery and linked to project.
5. User can iterate, remix or export to Dev Studio.

## Notes

- Higgsfield should be an optional integration, not a core dependency.
- API keys stored encrypted.
- Cost tracking per generation.

## Related

- [[../10_Architecture/10_Media_Forge]]
- [[../10_Architecture/16_Integration_Layer]]
- [[../40_Roadmap/Phase_6_Media_Omnichannel]]
