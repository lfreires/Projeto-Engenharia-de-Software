const PROJECT_NAME = "E-commerce API";

const MOCK_RESPONSE_TEMPLATE = (query: string) =>
  `Com base nos documentos indexados do projeto ${PROJECT_NAME}, posso confirmar que "${query}" é uma informação relevante. Para uma análise mais detalhada, recomendo consultar os arquivos da última ingestão ou refinar a pergunta com mais contexto.`;

/**
 * Sends a user message and returns an AI response.
 * Currently mocked — replace the body with a real API call when the backend is ready.
 */
export async function sendMessage(userMessage: string): Promise<string> {
  await new Promise((resolve) => setTimeout(resolve, 1800));
  return MOCK_RESPONSE_TEMPLATE(userMessage);
}
