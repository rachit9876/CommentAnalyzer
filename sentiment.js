let SENTIMENT = {};

fetch("sentiment.json")
  .then(r => r.json())
  .then(data => SENTIMENT = data);

const CONTRAST_WORDS = new Set(["but", "however", "though", "although", "yet"]);
const NEGATIONS = new Set(["not", "never", "no", "n't"]);

const TOKEN_REGEX = /(?:[<>]?[:;=8][\-o*']?[\)\]\(\[dDpP\/:\}{@|\\]|[\)\]\(\[dDpP\/:\}{@|\\][\-o*']?[:;=8][<>]?|\b\w+\b)/gi;

function tokenize(text) {
  return text.toLowerCase().match(TOKEN_REGEX) || [];
}

function applyContrast(tokens) {
  for (let i = 0; i < tokens.length; i++) {
    if (CONTRAST_WORDS.has(tokens[i])) {
      return tokens.slice(i + 1);
    }
  }
  return tokens;
}

function analyzeSentiment(text) {
  let tokens = tokenize(text);
  tokens = applyContrast(tokens);

  let score = 0;
  let hits = [];
  let negate = false;

  for (let t of tokens) {
    if (NEGATIONS.has(t)) {
      negate = true;
      continue;
    }

    if (SENTIMENT[t] !== undefined) {
      let val = SENTIMENT[t];
      if (negate) {
        val = -val;
        negate = false;
      }

      score += val;
      hits.push([t, val]);
    }
  }

  const confidence = Math.tanh(score / 5);

  let label = "NEUTRAL";
  if (score > 0.5) label = "POSITIVE";
  else if (score < -0.5) label = "NEGATIVE";

  return {
    text,
    label,
    score: Number(score.toFixed(2)),
    confidence: Number(confidence.toFixed(2)),
    matched_tokens: hits
  };
}
