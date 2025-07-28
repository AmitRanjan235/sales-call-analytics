import logging
import os
import re
from typing import Any, Dict, List, Optional

import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

logger = logging.getLogger(__name__)


class AIInsightModule:
    def __init__(self):
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        # Use a more reliable sentiment analysis model for testing
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                top_k=None,
            )
        except Exception as e:
            logger.warning(f"Failed to load sentiment model: {e}")
            self.sentiment_pipeline = None

        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate sentence embedding for the given text."""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment and return score between -1 and 1."""
        if not self.sentiment_pipeline:
            return 0.0

        try:
            results = self.sentiment_pipeline(text)
            logger.debug(f"Sentiment pipeline results for '{text[:50]}': {results}")

            # Handle different model outputs
            # Results format: [[{label: 'POSITIVE', score: 0.99}, {label: 'NEGATIVE', score: 0.01}]]
            if (
                isinstance(results, list)
                and len(results) > 0
                and isinstance(results[0], list)
            ):
                # For distilbert model (POSITIVE/NEGATIVE labels)
                sentiment_score = 0.0
                for result in results[0]:  # Access the inner list
                    if result["label"] == "NEGATIVE":
                        sentiment_score -= result["score"]
                    elif result["label"] == "POSITIVE":
                        sentiment_score += result["score"]
                    # For older models with LABEL_X format
                    elif result["label"] == "LABEL_0":  # Negative
                        sentiment_score -= result["score"]
                    elif result["label"] == "LABEL_2":  # Positive
                        sentiment_score += result["score"]
                    # LABEL_1 or neutral contributes 0

                return max(-1.0, min(1.0, sentiment_score))

            return 0.0
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0

    def calculate_agent_talk_ratio(self, transcript: str) -> float:
        """Calculate the ratio of agent words to total words."""
        try:
            # Simple heuristic: assume lines starting with "Agent:" or "A:" are agent speech
            agent_patterns = [r"^Agent:", r"^A:", r"^AGENT:", r"^agent:"]
            customer_patterns = [r"^Customer:", r"^C:", r"^CUSTOMER:", r"^customer:"]

            lines = transcript.split("\n")
            agent_words = 0
            customer_words = 0

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                is_agent = any(re.match(pattern, line) for pattern in agent_patterns)
                is_customer = any(
                    re.match(pattern, line) for pattern in customer_patterns
                )

                # Remove speaker labels and count words
                clean_line = re.sub(
                    r"^(Agent|A|Customer|C|AGENT|CUSTOMER|agent|customer):\s*", "", line
                )
                words = len(re.findall(r"\b\w+\b", clean_line))

                if is_agent:
                    agent_words += words
                elif is_customer:
                    customer_words += words
                else:
                    # If no clear speaker, split 50/50
                    agent_words += words // 2
                    customer_words += words - (words // 2)

            total_words = agent_words + customer_words
            return agent_words / total_words if total_words > 0 else 0.5

        except Exception as e:
            logger.error(f"Error calculating agent talk ratio: {e}")
            return 0.5

    def find_similar_calls(
        self,
        target_embedding: List[float],
        call_embeddings: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Find the most similar calls based on cosine similarity."""
        try:
            if not target_embedding or not call_embeddings:
                return []

            target_emb = np.array(target_embedding).reshape(1, -1)
            similarities = []

            for call_data in call_embeddings:
                if not call_data.get("embedding"):
                    continue

                call_emb = np.array(call_data["embedding"]).reshape(1, -1)
                similarity = cosine_similarity(target_emb, call_emb)[0][0]

                similarities.append(
                    {
                        "call_id": call_data["call_id"],
                        "agent_id": call_data["agent_id"],
                        "similarity_score": float(similarity),
                        "transcript_preview": call_data["transcript"][:200] + "...",
                    }
                )

            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Error finding similar calls: {e}")
            return []

    def generate_coaching_nudges(
        self, transcript: str, sentiment_score: float, talk_ratio: float
    ) -> List[str]:
        """Generate coaching nudges using LLM or rule-based approach."""
        nudges = []

        try:
            if self.openai_client:
                # Use OpenAI for more sophisticated nudges
                prompt = f"""
                Based on this sales call analysis:
                - Sentiment score: {sentiment_score:.2f} (-1 to 1 scale)
                - Agent talk ratio: {talk_ratio:.2f}
                - Transcript preview: {transcript[:300]}...
                
                Generate 3 brief coaching tips (max 40 words each) for the sales agent.
                Focus on practical improvements.
                """

                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=200,
                        temperature=0.7,
                    )

                    content = response.choices[0].message.content
                    nudges = [
                        line.strip() for line in content.split("\n") if line.strip()
                    ][:3]
                except Exception as e:
                    logger.warning(f"OpenAI API error, falling back to rule-based: {e}")
                    nudges = []

            # Fallback to rule-based nudges if OpenAI fails or isn't available
            if not nudges:
                nudges = self._generate_rule_based_nudges(sentiment_score, talk_ratio)

            # Ensure nudges are within word limit
            return [nudge[:40] for nudge in nudges[:3]]

        except Exception as e:
            logger.error(f"Error generating coaching nudges: {e}")
            return [
                "Focus on active listening",
                "Ask more open questions",
                "Empathize with customer needs",
            ]

    def _generate_rule_based_nudges(
        self, sentiment_score: float, talk_ratio: float
    ) -> List[str]:
        """Generate rule-based coaching nudges."""
        nudges = []

        if sentiment_score < -0.3:
            nudges.append("Address customer concerns empathetically")
        elif sentiment_score < 0:
            nudges.append("Use positive language to improve mood")

        if talk_ratio > 0.7:
            nudges.append("Listen more, talk less - aim for balance")
        elif talk_ratio < 0.4:
            nudges.append("Take more initiative in conversation")

        if len(nudges) < 3:
            general_nudges = [
                "Ask discovery questions",
                "Confirm understanding regularly",
                "Focus on customer value",
                "Use customer's name more often",
                "Summarize key points clearly",
            ]
            nudges.extend(general_nudges[: 3 - len(nudges)])

        return nudges[:3]
