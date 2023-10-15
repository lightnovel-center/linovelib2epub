import { VercelRequest, VercelResponse } from '@vercel/node';
import https from 'https';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  try {
    const nonAsciiDict = await decipher();
    return res.status(200).json(nonAsciiDict);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    return res.status(500).json({ error: 'Internal Server Error' });
  }
}

async function getJS() {
  const url = 'https://w.linovelib.com/themes/zhmb/js/readtools.js';

  return new Promise<string>((resolve, reject) => {
    https.get(url, (response) => {
      let data = '';

      response.on('data', (chunk) => {
        data += chunk;
      });

      response.on('end', () => {
        const reg = /\['jsjiami.com.v4'\](.*?)\('jsjiami.com.v4'\);/s;
        const match = data.match(reg);

        if (match) {
          const extractedContent = match[1].trim();
          resolve(extractedContent);
        } else {
          reject(new Error('未找到映射表'));
        }
      });
    }).on('error', (error) => {
      reject(error);
    });
  });
}

async function decipher() {
  try {
    const inputString = await getJS();
    const match = inputString.match(/ull,"(.*?)"\[/);

    if (match && match.length > 1) {
      const extractedString = match[1];
      const plain_text = String.fromCharCode.apply(null, extractedString.split(/[a-zA-Z]{1,}/));

      const nonAsciiDict = extractNonAsciiToDict(plain_text);
      console.log(nonAsciiDict);
      return nonAsciiDict;
    } else {
      throw new Error('未找到匹配的字符串');
    }
  } catch (error) {
    throw error;
  }
}

function extractNonAsciiToDict(inputStr: string) {
  const nonAsciiChars = [...inputStr].filter((char) => char.charCodeAt(0) > 127);
  const resultDict: { [key: string]: string } = {};

  for (let i = 0; i < nonAsciiChars.length; i += 2) {
    const char1 = nonAsciiChars[i];
    const char2 = i + 1 < nonAsciiChars.length ? nonAsciiChars[i + 1] : null;

    const key = escapeUnicode(char1);
    const value = char2 !== null ? char2 : '';

    resultDict[key] = value;
  }

  return resultDict;
}

function escapeUnicode(char: string) {
  return '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0');
}