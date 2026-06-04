// Polyfill de crypto.randomUUID para contexto NÃO-seguro (HTTP puro acessado por IP).
//
// crypto.randomUUID() só é exposto pelo navegador em "secure context" (HTTPS ou
// localhost). O TipTap chama crypto.randomUUID() ao montar o editor; quando o app
// é servido por http://<ip> ele não existe e o editor quebra com tela branca.
// crypto.getRandomValues() — diferente de randomUUID — está disponível mesmo fora
// de secure context, então geramos um UUIDv4 a partir dele.
//
// É inofensivo sob HTTPS: o bloco só roda quando randomUUID já não existe. Quando
// o domínio + SSL entrarem (Fase 2), o navegador passa a expor o nativo e este
// polyfill vira no-op.
if (typeof crypto !== 'undefined' && typeof crypto.randomUUID !== 'function') {
  crypto.randomUUID = (() => {
    const bytes = crypto.getRandomValues(new Uint8Array(16))
    bytes[6] = (bytes[6] & 0x0f) | 0x40 // versão 4
    bytes[8] = (bytes[8] & 0x3f) | 0x80 // variante RFC 4122
    const h = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`
  }) as Crypto['randomUUID']
}
