import type { InspirationIdea, Trend } from '../types/trend';

export const mockTrends: Trend[] = [
  {
    id: 'trend-ai-search-habits',
    topicName: 'AI 搜尋取代傳統搜尋',
    summary: '越來越多人改用 AI 工具查資料，引發搜尋習慣與內容 SEO 的討論。',
    heatScore: 92,
    growthRate: 48,
    momentum: 'rising',
    lifecycleStage: 'growing',
    platforms: ['threads', 'news', 'dcard'],
    keywords: ['AI 搜尋', 'SEO', 'ChatGPT', '內容策略'],
    suitableIndustries: ['科技業', '教育業', '行銷顧問', '內容平台'],
    unsuitableIndustries: ['與數位服務無關且無觀點切入的品牌'],
    riskLevel: 'medium',
    riskNote: '容易流於焦慮式標題，需避免誇大 AI 取代效果。',
    whyTrending: '使用者實際搜尋行為正在改變，品牌與內容創作者開始擔心曝光方式被重塑。',
    contentAngles: ['AI 搜尋時代的內容策略', '品牌如何被 AI 找到', '傳統 SEO 還有沒有用'],
    trendSignal: {
      heatScore: 92,
      growthRate: 48,
      momentum: 'rising',
      lifecycleStage: 'growing',
      platforms: ['threads', 'news', 'dcard'],
      riskLevel: 'medium',
      riskNote: '議題仍在升溫，但需要專業脈絡避免空泛。'
    },
    representativeContents: [
      {
        id: 'content-ai-search-1',
        platformName: 'Threads',
        platformCode: 'threads',
        externalContentId: 'th-ai-search-001',
        title: '你現在還會用 Google 搜資料嗎？',
        body: '很多人開始直接問 AI，搜尋結果頁好像越來越少被打開。',
        url: 'https://example.com/threads/ai-search',
        publishedAt: '2026-05-31T08:10:00+08:00',
        likes: 4200,
        comments: 680,
        shares: 310,
        contentType: 'thread'
      }
    ]
  },
  {
    id: 'trend-late-night-food-map',
    topicName: '深夜美食地圖',
    summary: '網友整理深夜仍營業的美食清單，帶動在地餐飲與宵夜討論。',
    heatScore: 87,
    growthRate: 35,
    momentum: 'rising',
    lifecycleStage: 'viral',
    platforms: ['dcard', 'threads', 'instagram'],
    keywords: ['宵夜', '深夜美食', '在地推薦', '美食地圖'],
    suitableIndustries: ['餐飲業', '旅遊休閒', '外送平台', '地方型商家'],
    unsuitableIndustries: ['嚴肅金融服務', '高風險醫療議題品牌'],
    riskLevel: 'low',
    riskNote: '需注意營業資訊正確性，避免推薦已歇業店家。',
    whyTrending: '生活實用資訊容易被收藏與分享，且能引發城市與在地認同。',
    contentAngles: ['城市深夜指南', '小店故事', '下班後療癒路線'],
    trendSignal: {
      heatScore: 87,
      growthRate: 35,
      momentum: 'rising',
      lifecycleStage: 'viral',
      platforms: ['dcard', 'threads', 'instagram'],
      riskLevel: 'low',
      riskNote: '適合快速跟進，但資訊需要核對。'
    },
    representativeContents: [
      {
        id: 'content-food-1',
        platformName: 'Dcard',
        platformCode: 'dcard',
        externalContentId: 'dc-food-001',
        title: '台北深夜還能吃什麼？',
        body: '整理幾間凌晨還開的店，救救半夜加班的人。',
        url: 'https://example.com/dcard/late-night-food',
        publishedAt: '2026-05-31T23:30:00+08:00',
        likes: 3800,
        comments: 540,
        shares: 720,
        contentType: 'list'
      }
    ]
  },
  {
    id: 'trend-housing-rent-pressure',
    topicName: '租屋壓力與居住焦慮',
    summary: '房租、通勤與生活品質討論升溫，年輕族群分享租屋困境。',
    heatScore: 84,
    growthRate: 28,
    momentum: 'stable',
    lifecycleStage: 'growing',
    platforms: ['dcard', 'ptt', 'news'],
    keywords: ['租屋', '房價', '通勤', '居住正義'],
    suitableIndustries: ['房地產', '金融業', '居家生活', '保險業'],
    unsuitableIndustries: ['娛樂化語氣品牌', '不具備專業觀點的跟風內容'],
    riskLevel: 'high',
    riskNote: '涉及民生與政策議題，切入時需避免嘲諷或過度簡化。',
    whyTrending: '租屋成本與薪資落差引發共鳴，新聞與論壇討論互相放大。',
    contentAngles: ['租屋檢查清單', '通勤成本試算', '小宅收納與生活品質'],
    trendSignal: {
      heatScore: 84,
      growthRate: 28,
      momentum: 'stable',
      lifecycleStage: 'growing',
      platforms: ['dcard', 'ptt', 'news'],
      riskLevel: 'high',
      riskNote: '社會議題敏感度高，建議採資訊型或同理型切入。'
    },
    representativeContents: [
      {
        id: 'content-rent-1',
        platformName: 'PTT',
        platformCode: 'ptt',
        externalContentId: 'ptt-rent-001',
        title: '租屋花掉薪水三分之一正常嗎？',
        body: '最近看房真的很有感，價格一直上去但空間越來越小。',
        url: 'https://example.com/ptt/rent-pressure',
        publishedAt: '2026-05-30T21:00:00+08:00',
        likes: 1800,
        comments: 920,
        shares: 260,
        contentType: 'discussion'
      }
    ]
  },
  {
    id: 'trend-retro-camera-filter',
    topicName: '復古相機濾鏡回潮',
    summary: '低飽和、底片感與舊相機濾鏡再度流行，帶動拍照與穿搭內容。',
    heatScore: 79,
    growthRate: 22,
    momentum: 'rising',
    lifecycleStage: 'emerging',
    platforms: ['instagram', 'threads'],
    keywords: ['復古濾鏡', '底片感', '相機 App', '穿搭'],
    suitableIndustries: ['美妝保養', '服飾', '攝影器材', '旅遊休閒'],
    unsuitableIndustries: ['嚴肅 B2B 服務'],
    riskLevel: 'low',
    riskNote: '風險低，但內容容易同質化，需要明確視覺風格。',
    whyTrending: '使用者對高精緻照片疲乏，復古感提供更生活化與情緒化的表達。',
    contentAngles: ['一週復古穿搭', '城市底片感路線', '品牌視覺前後對比'],
    trendSignal: {
      heatScore: 79,
      growthRate: 22,
      momentum: 'rising',
      lifecycleStage: 'emerging',
      platforms: ['instagram', 'threads'],
      riskLevel: 'low',
      riskNote: '適合視覺型品牌早期測試。'
    },
    representativeContents: [
      {
        id: 'content-camera-1',
        platformName: 'Instagram',
        platformCode: 'instagram',
        externalContentId: 'ig-camera-001',
        title: '最近大家都在用的底片感濾鏡',
        body: '不用真的買底片機，也能拍出有年代感的照片。',
        url: 'https://example.com/instagram/retro-filter',
        publishedAt: '2026-05-31T16:20:00+08:00',
        likes: 9600,
        comments: 430,
        shares: 1100,
        contentType: 'image'
      }
    ]
  },
  {
    id: 'trend-celebrity-apology-template',
    topicName: '名人道歉聲明模板化',
    summary: '多起名人爭議後，網友開始討論道歉聲明是否越來越公式化。',
    heatScore: 73,
    growthRate: -18,
    momentum: 'cooling',
    lifecycleStage: 'declining',
    platforms: ['threads', 'news', 'ptt'],
    keywords: ['名人爭議', '道歉聲明', '公關危機', '模板化'],
    suitableIndustries: ['公關顧問', '媒體評論', '職場溝通教育'],
    unsuitableIndustries: ['一般消費品牌', '餐飲業', '親子品牌'],
    riskLevel: 'high',
    riskNote: '爭議高且熱度正在下降，不適合娛樂化跟風。',
    whyTrending: '連續事件讓網友注意到危機處理語言的相似性，但討論熱度已開始轉弱。',
    contentAngles: ['危機溝通分析', '聲明文字拆解', '品牌信任如何修復'],
    trendSignal: {
      heatScore: 73,
      growthRate: -18,
      momentum: 'cooling',
      lifecycleStage: 'declining',
      platforms: ['threads', 'news', 'ptt'],
      riskLevel: 'high',
      riskNote: '適合專業分析，不適合輕浮借勢。'
    },
    representativeContents: [
      {
        id: 'content-apology-1',
        platformName: 'News',
        platformCode: 'news',
        externalContentId: 'news-apology-001',
        title: '道歉聲明為什麼越來越像？',
        body: '公關危機中的文字選擇，正在成為網友討論焦點。',
        url: 'https://example.com/news/apology-template',
        publishedAt: '2026-05-29T12:00:00+08:00',
        likes: 2100,
        comments: 760,
        shares: 520,
        contentType: 'news'
      }
    ]
  }
];

export const mockInspirationIdeas: InspirationIdea[] = [
  {
    id: 'idea-ai-search-1',
    trendId: 'trend-ai-search-habits',
    ideaTitle: '你的品牌會被 AI 推薦嗎？',
    ideaSummary: '從搜尋習慣改變切入，協助使用者理解品牌內容如何被 AI 理解。',
    contentAngle: '教育型趨勢解析',
    openingHook: '如果你的客戶不再 Google，而是直接問 AI，你的品牌還會被看見嗎？',
    suggestedPlatforms: ['Threads', 'LinkedIn', '電子報'],
    suggestedFormat: '長文或圖文懶人包',
    notRecommendedApproach: '不要用恐嚇式標題宣稱傳統搜尋已死亡。',
    riskNote: '需要搭配具體案例，避免變成空泛 AI 焦慮。'
  }
];
