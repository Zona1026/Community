import type {
  AiAnalysis,
  AiAnalysisInput,
  AiTone,
  GeneratedCopy,
  PostAngle,
} from '../../types/aiAnalysis';

const CONTROVERSY_KEYWORDS = [
  '爭議',
  '風險',
  '炎上',
  '隱私',
  '誤導',
  '偏見',
  '資安',
  '個資',
  '抄襲',
  '版權',
];

function getMomentumLabel(momentum: string): string {
  if (momentum === 'rising') {
    return '上升';
  }

  if (momentum === 'stable') {
    return '穩定';
  }

  return '偏弱';
}

function createFallbackCopy(input: AiAnalysisInput): string {
  const angleIntro: Record<PostAngle, string> = {
    教學: `用教學角度拆解「${input.topic}」`,
    觀點: `從觀點文章切入「${input.topic}」`,
    懶人包: `整理一篇「${input.topic}」懶人包`,
  };
  const toneEnding: Record<AiTone, string> = {
    專業: '語氣保持專業，適合放在 LinkedIn 或品牌內容。',
    輕鬆: '語氣可以更口語，適合社群貼文與短影音腳本。',
    犀利: '語氣要有明確立場，適合做成觀點型貼文。',
  };

  return `${angleIntro[input.angle]}：目前分數 ${input.score}，動能為${getMomentumLabel(
    input.momentum,
  )}。建議先用一個真實痛點開場，再接上案例與可執行做法。${toneEnding[input.tone]}`;
}

function createGeneratedCopy(input: AiAnalysisInput): GeneratedCopy {
  return {
    id: `${input.topicId}-${input.tone}-${input.angle}-${Date.now()}`,
    tone: input.tone,
    angle: input.angle,
    text: createFallbackCopy(input),
    createdAt: new Date().toISOString(),
  };
}

function hasControversySignal(input: AiAnalysisInput): boolean {
  const searchText = [
    input.topic,
    input.summary,
    input.insight,
    ...input.topicTags,
    ...input.relatedContent.flatMap((content) => [
      content.title,
      content.text,
    ]),
  ]
    .join(' ')
    .toLowerCase();

  return CONTROVERSY_KEYWORDS.some((keyword) =>
    searchText.includes(keyword.toLowerCase()),
  );
}

function createContentIdeas(input: AiAnalysisInput): string[] {
  return [
    `把「${input.topic}」整理成 ${input.angle} 內容，先講使用者痛點，再補上操作建議。`,
    `引用 ${input.source} 的討論脈絡，說明這個話題為什麼現在值得追蹤。`,
    `用${input.tone}語氣做成三段式貼文：問題、觀察、可執行下一步。`,
  ];
}

export function createAiAnalysis(input: AiAnalysisInput): AiAnalysis {
  try {
    const momentumLabel = getMomentumLabel(input.momentum);
    const controversyWarning = hasControversySignal(input)
      ? '此話題可能包含爭議或高敏感訊號，建議發布前確認資料來源與用詞。'
      : '目前未偵測到明顯爭議訊號，仍建議保留人工檢查。';

    return {
      shortSummary: `${input.topic} 目前分數 ${input.score}，趨勢動能為${momentumLabel}。`,
      fullSummary: `${input.summary} 目前共整合 ${input.contentCount} 筆內容，主要來源為 ${input.source}。可優先用「${input.angle}」角度整理，並維持「${input.tone}」語氣。`,
      controversyWarning,
      contentIdeas: createContentIdeas(input),
      generatedCopies: [createGeneratedCopy(input)],
      provider: 'mock',
      isFallback: true,
    };
  } catch {
    return {
      shortSummary: 'AI mock 分析暫時無法產生。',
      fullSummary: '系統仍可顯示原始話題資訊，不影響 Demo 主流程。',
      controversyWarning: '爭議提醒暫時無法產生，請以人工檢查為準。',
      contentIdeas: [],
      generatedCopies: [],
      provider: 'mock',
      isFallback: true,
      errorMessage: 'AI mock 分析發生錯誤，已使用 fallback。',
    };
  }
}
