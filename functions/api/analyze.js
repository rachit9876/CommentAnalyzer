const EMOJI_AND_SLANG = {
  // Emojis
  "🔥": 3, "❤️": 3, "💖": 3, "😍": 3, "🥰": 3, "👏": 2, "🙌": 2, "🎉": 2, "👍": 2, "💯": 3, "⭐": 2, "✨": 2, "🚀": 2,
  "💀": -1, "💩": -3, "🤡": -3, "👎": -2, "🗑️": -3, "🤮": -3, "😡": -2, "🤬": -3, "😭": 0.5, "🤦": -2, "💔": -2, "🥱": -1,
  // YouTube & Internet Slang
  "goat": 3, "fire": 3, "peak": 3, "masterpiece": 3, "w": 2, "l": -2, "mid": -2, "scam": -3,
  "trash": -3, "crap": -2, "cap": -2, "nocap": 2, "cooked": -2, "banger": 3, "breathtaking": 3,
  "legendary": 3, "clutch": 2, "underrated": 2, "overrated": -2, "clickbait": -3, "cringe": -2.5
};

const CONTRAST_WORDS = new Set(["but", "however", "though", "although", "yet"]);
const NEGATIONS = new Set(["not", "never", "no", "n't", "neither", "nor", "without", "lack", "don't", "doesn't", "didn't", "won't", "can't", "couldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't"]);

const TOKEN_REGEX = /(\p{Extended_Pictographic}|[<>]?[:;=8][\-o*']?[\)\]\(\[dDpP\/:\}{@|\\]|[\)\]\(\[dDpP\/:\}{@|\\][\-o*']?[:;=8][<>]?|\b\w+\b)/gu;

function tokenize(text) {
  if (!text) return [];
  return text.toLowerCase().match(TOKEN_REGEX) || [];
}

export async function onRequestPost(context) {
  try {
    const request = context.request;
    
    let body;
    try {
      body = await request.json();
    } catch (e) {
      return new Response(JSON.stringify({ error: "Invalid JSON body" }), { 
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }
    
    if (!body.text || typeof body.text !== 'string') {
      return new Response(JSON.stringify({ error: "Missing or invalid 'text' field in JSON body" }), { 
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const text = body.text;

    // Fetch sentiment.json from the static assets
    const url = new URL(request.url);
    const assetResponse = await context.env.ASSETS.fetch(new URL('/sentiment.json', url.origin));
    if (!assetResponse.ok) {
      throw new Error("Failed to load sentiment dictionary");
    }
    const SENTIMENT = await assetResponse.json();

    let tokens = tokenize(text);

    let score = 0;
    let hits = [];
    let negateCount = 0;
    let contrastApplied = false;

    for (let i = 0; i < tokens.length; i++) {
      const t = tokens[i];

      if (CONTRAST_WORDS.has(t)) {
        negateCount = 0;
        contrastApplied = true;
        continue;
      }

      if (NEGATIONS.has(t) || t.endsWith("n't")) {
        negateCount = 3;
        continue;
      }

      let val = undefined;
      if (EMOJI_AND_SLANG[t] !== undefined) {
        val = EMOJI_AND_SLANG[t];
      } else if (SENTIMENT[t] !== undefined) {
        val = SENTIMENT[t];
      }

      if (val !== undefined) {
        if (negateCount > 0) {
          val = -val;
        }
        if (contrastApplied) {
          val = val * 1.25;
        }

        score += val;
        hits.push([t, Number(val.toFixed(2))]);
      }

      if (negateCount > 0) {
        negateCount--;
      }
    }

    const confidence = Math.tanh(Math.abs(score) / 5);

    let label = "NEUTRAL";
    if (score > 0.3) label = "POSITIVE";
    else if (score < -0.3) label = "NEGATIVE";

    const result = {
      text,
      label,
      score: Number(score.toFixed(2)),
      confidence: Number(confidence.toFixed(2)),
      matched_tokens: hits
    };

    return new Response(JSON.stringify(result), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { 
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    }
  });
}

