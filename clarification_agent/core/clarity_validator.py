"""
Enhanced clarity validation system with configurable rules.
Integrates with existing LLMHelper and supports multiple validation types.
"""
import re
from typing import Dict, Any, List, Tuple, Optional
from clarification_agent.utils.llm_helper import LLMHelper
from clarification_agent.config.node_config import get_node_config_manager


class ClarityValidator:
    """Validates user responses based on configurable rules."""
    
    def __init__(self, llm_helper: Optional[LLMHelper] = None):
        self.llm_helper = llm_helper or LLMHelper()
        self.config_manager = get_node_config_manager()
    
    def validate_response(self, node_id: str, user_response: str, context: Optional[Dict[str, Any]] = None) -> Tuple[bool, float, str]:
        """
        Validate user response against node-specific clarity rules.
        
        Args:
            node_id: Current node identifier
            user_response: User's response text
            context: Additional context (project data, etc.)
            
        Returns:
            Tuple of (is_clear, clarity_score, feedback_message)
        """
        node_config = self.config_manager.get_node_config(node_id)
        clarity_rules = node_config.get("clarity_rules", [])
        
        if not clarity_rules:
            # Fallback to simple validation
            return self._simple_validation(user_response)
        
        # Process each rule
        total_score = 0.0
        rule_count = 0
        feedback_messages = []
        
        for rule in clarity_rules:
            rule_type = rule["type"]
            is_valid, score, message = self._apply_rule(rule_type, rule, user_response, context)
            
            if not is_valid:
                return False, score, message
            
            total_score += score
            rule_count += 1
            
            if message:
                feedback_messages.append(message)
        
        # Calculate average score
        avg_score = total_score / rule_count if rule_count > 0 else 0.5
        
        # Determine if clear based on average score
        is_clear = avg_score >= 0.7  # Default threshold
        
        feedback = " ".join(feedback_messages) if feedback_messages else "Response looks good!"
        
        return is_clear, avg_score, feedback
    
    def _apply_rule(self, rule_type: str, rule: Dict[str, Any], user_response: str, context: Optional[Dict[str, Any]]) -> Tuple[bool, float, str]:
        """Apply a specific validation rule."""
        
        if rule_type == "min_words":
            return self._validate_min_words(rule, user_response)
        
        elif rule_type == "specificity_score":
            return self._validate_specificity_score(rule, user_response)
        
        elif rule_type == "required_entities":
            return self._validate_required_entities(rule, user_response)
        
        elif rule_type == "min_features":
            return self._validate_min_features(rule, user_response)
        
        elif rule_type == "feature_clarity":
            return self._validate_feature_clarity(rule, user_response)
        
        elif rule_type == "min_exclusions":
            return self._validate_min_exclusions(rule, user_response)
        
        elif rule_type == "tech_completeness":
            return self._validate_tech_completeness(rule, user_response)
        
        elif rule_type == "tech_compatibility":
            return self._validate_tech_compatibility(rule, user_response)
        
        elif rule_type in ["architecture_approval", "task_approval", "final_approval"]:
            return self._validate_approval(rule, user_response)
        
        else:
            # Unknown rule type, skip
            return True, 0.7, ""
    
    def _validate_min_words(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate minimum word count."""
        word_count = len(user_response.split())
        threshold = rule.get("threshold", 3)
        
        if word_count < threshold:
            return False, 0.3, rule.get("message", f"Please provide at least {threshold} words")
        
        return True, min(1.0, word_count / (threshold * 2)), ""
    
    def _validate_specificity_score(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate specificity using LLM."""
        prompt = rule.get("openrouter_prompt", "").format(response=user_response)
        threshold = rule.get("threshold", 0.6)
        
        try:
            # Call LLM for specificity score
            messages = [
                {"role": "system", "content": "You are an AI that rates text specificity. Return only a number between 0 and 1."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm_helper._call_openrouter(messages, temperature=0.3)
            
            if response:
                # Extract number from response
                score_match = re.search(r'0?\.\d+|[01]', response)
                if score_match:
                    score = float(score_match.group())
                    if score < threshold:
                        return False, score, rule.get("message", "Please be more specific")
                    return True, score, ""
        
        except Exception as e:
            print(f"Error in specificity validation: {e}")
        
        # Fallback to simple heuristic
        return self._simple_specificity_check(user_response, threshold)
    
    def _validate_required_entities(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate presence of required entities."""
        entities = rule.get("entities", [])
        response_lower = user_response.lower()
        
        found_entities = []
        for entity in entities:
            if entity.lower() in response_lower:
                found_entities.append(entity)
        
        if len(found_entities) < len(entities):
            missing = [e for e in entities if e not in found_entities]
            return False, len(found_entities) / len(entities), rule.get("message", f"Please specify: {', '.join(missing)}")
        
        return True, 1.0, ""
    
    def _validate_min_features(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate minimum number of features mentioned."""
        threshold = rule.get("threshold", 2)
        
        # Simple heuristic: count lines or comma-separated items
        features = []
        
        # Try to extract features from lines
        lines = [line.strip() for line in user_response.split('\n') if line.strip()]
        if len(lines) >= threshold:
            features = lines
        else:
            # Try comma-separated
            items = [item.strip() for item in user_response.split(',') if item.strip()]
            if len(items) >= threshold:
                features = items
        
        if len(features) < threshold:
            return False, len(features) / threshold, rule.get("message", f"Please specify at least {threshold} features")
        
        return True, min(1.0, len(features) / threshold), ""
    
    def _validate_feature_clarity(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate clarity of feature descriptions."""
        return self._validate_specificity_score(rule, user_response)
    
    def _validate_min_exclusions(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate minimum number of exclusions."""
        threshold = rule.get("threshold", 1)
        
        # Look for negative indicators
        negative_patterns = [
            r"not?\s+\w+", r"no\s+\w+", r"exclude\s+\w+", r"without\s+\w+",
            r"don't\s+\w+", r"won't\s+\w+", r"skip\s+\w+"
        ]
        
        exclusions = []
        for pattern in negative_patterns:
            matches = re.findall(pattern, user_response, re.IGNORECASE)
            exclusions.extend(matches)
        
        # Also check for explicit lists
        lines = [line.strip() for line in user_response.split('\n') if line.strip()]
        if len(lines) > 0:
            exclusions.extend(lines)
        
        if len(exclusions) < threshold:
            return False, len(exclusions) / threshold, rule.get("message", f"Please specify at least {threshold} item to exclude")
        
        return True, min(1.0, len(exclusions) / threshold), ""
    
    def _validate_tech_completeness(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate completeness of tech stack."""
        required_categories = rule.get("required_categories", [])
        response_lower = user_response.lower()
        
        found_categories = []
        category_keywords = {
            "frontend": ["react", "vue", "angular", "frontend", "client", "ui", "html", "css", "javascript"],
            "backend": ["node", "python", "java", "backend", "server", "api", "express", "django", "flask"],
            "database": ["mysql", "postgres", "mongodb", "database", "db", "sql", "nosql", "redis"]
        }
        
        for category in required_categories:
            keywords = category_keywords.get(category, [category])
            if any(keyword in response_lower for keyword in keywords):
                found_categories.append(category)
        
        if len(found_categories) < len(required_categories):
            missing = [c for c in required_categories if c not in found_categories]
            return False, len(found_categories) / len(required_categories), rule.get("message", f"Please specify: {', '.join(missing)}")
        
        return True, 1.0, ""
    
    def _validate_tech_compatibility(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate tech stack compatibility using LLM."""
        return self._validate_specificity_score(rule, user_response)
    
    def _validate_approval(self, rule: Dict[str, Any], user_response: str) -> Tuple[bool, float, str]:
        """Validate user approval/satisfaction."""
        response_lower = user_response.lower()
        
        # Look for positive indicators
        positive_indicators = ["yes", "ok", "good", "approve", "confirm", "agree", "looks good", "perfect"]
        negative_indicators = ["no", "not", "change", "modify", "different", "wrong"]
        
        positive_score = sum(1 for indicator in positive_indicators if indicator in response_lower)
        negative_score = sum(1 for indicator in negative_indicators if indicator in response_lower)
        
        if negative_score > positive_score:
            return False, 0.3, "Please let me know what you'd like to change"
        
        if positive_score > 0:
            return True, 0.9, ""
        
        # Use LLM for more nuanced approval detection
        return self._validate_specificity_score(rule, user_response)
    
    def _simple_validation(self, user_response: str) -> Tuple[bool, float, str]:
        """Simple fallback validation."""
        word_count = len(user_response.split())
        
        if word_count < 2:
            return False, 0.2, "Please provide more details"
        elif word_count < 5:
            return True, 0.6, "Consider adding more details"
        else:
            return True, 0.8, ""
    
    def _simple_specificity_check(self, user_response: str, threshold: float) -> Tuple[bool, float, str]:
        """Simple heuristic for specificity."""
        word_count = len(user_response.split())
        unique_words = len(set(user_response.lower().split()))
        
        # Simple specificity score based on length and uniqueness
        specificity = min(1.0, (word_count * unique_words) / 100)
        
        if specificity < threshold:
            return False, specificity, "Please be more specific"
        
        return True, specificity, ""