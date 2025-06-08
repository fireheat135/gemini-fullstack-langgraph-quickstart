"""
Fact Checking System
ファクトチェック・品質担保機能

機能:
1. 内容の事実確認システム
2. 信頼性のある情報源との照合
3. 誤情報検出アラート
4. 品質スコア算出
5. 最終品質チェックレポート
"""

import re
import json
import hashlib
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict, Counter

from .content_management_system import ArticleContent, ToneManner


class FactCheckStatus(Enum):
    """ファクトチェック状態"""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISPUTED = "disputed"
    NEEDS_REVIEW = "needs_review"
    FACT_ERROR = "fact_error"


class SourceReliability(Enum):
    """情報源信頼性"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class FactCheckType(Enum):
    """ファクトチェックタイプ"""
    SCIENTIFIC_NAME = "scientific_name"
    FLOWER_CHARACTERISTICS = "flower_characteristics"
    SEASONAL_INFO = "seasonal_info"
    CULTURAL_SIGNIFICANCE = "cultural_significance"
    CARE_INSTRUCTIONS = "care_instructions"
    HISTORICAL_INFO = "historical_info"


class QualityAspect(Enum):
    """品質評価観点"""
    FACTUAL_ACCURACY = "factual_accuracy"
    SOURCE_RELIABILITY = "source_reliability"
    CONTENT_COMPLETENESS = "content_completeness"
    CONSISTENCY = "consistency"
    READABILITY = "readability"


@dataclass
class TrustedSource:
    """信頼できる情報源"""
    source_id: str
    name: str
    url: str
    reliability_level: SourceReliability
    expertise_areas: List[str]
    verification_date: datetime
    
    def __post_init__(self):
        """バリデーション"""
        if not all([self.source_id, self.name, self.url]):
            raise ValueError("情報源の必須項目が不足しています")


@dataclass
class FactClaim:
    """事実主張"""
    claim_id: str
    text: str
    fact_type: FactCheckType
    confidence_score: float
    sources: List[str]
    extraction_date: datetime = field(default_factory=datetime.now)


@dataclass
class FactCheckResult:
    """ファクトチェック結果"""
    claim_id: str
    status: FactCheckStatus
    confidence_score: float
    verified_sources: List[str]
    conflicting_info: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class MisinformationAlert:
    """誤情報アラート"""
    alert_id: str
    severity: str  # HIGH, MEDIUM, LOW
    claim_text: str
    issue_description: str
    correction_suggestion: Optional[str] = None
    confidence_score: float = 0.0


@dataclass
class QualityMetric:
    """品質メトリック"""
    aspect: QualityAspect
    score: float  # 0-1
    weight: float  # 重み
    details: Dict[str, Any]


@dataclass
class QualityCheckReport:
    """品質チェックレポート"""
    article_id: str
    overall_quality_score: float
    fact_check_results: List[FactCheckResult]
    quality_metrics: List[QualityMetric]
    misinformation_alerts: List[MisinformationAlert]
    recommendations: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


class FactCheckingSystem:
    """
    ファクトチェック・品質担保システム
    記事の事実確認と品質評価を行う
    """
    
    def __init__(self):
        self.trusted_sources: Dict[str, TrustedSource] = {}
        self.fact_database: Dict[str, List[FactClaim]] = defaultdict(list)
        self.verification_patterns: Dict[str, List[str]] = {}
        
        # 初期化
        self._initialize_trusted_sources()
        self._initialize_verification_patterns()
        self._initialize_flower_facts_database()
    
    # ===== 信頼できる情報源管理 =====
    
    def add_trusted_source(self, source: TrustedSource):
        """信頼できる情報源追加"""
        self.trusted_sources[source.source_id] = source
    
    def get_trusted_sources(self, expertise_area: Optional[str] = None) -> List[TrustedSource]:
        """信頼できる情報源取得"""
        if not expertise_area:
            return list(self.trusted_sources.values())
        
        return [
            source for source in self.trusted_sources.values()
            if expertise_area in source.expertise_areas
        ]
    
    def evaluate_source_reliability(self, source_url: str) -> SourceReliability:
        """情報源信頼性評価"""
        # ドメインベースの信頼性評価
        reliable_domains = {
            "botanical.jp": SourceReliability.HIGH,
            "flowerpedia.org": SourceReliability.HIGH,
            "garden-academy.jp": SourceReliability.MEDIUM,
            "wikipedia.org": SourceReliability.MEDIUM,
        }
        
        for domain, reliability in reliable_domains.items():
            if domain in source_url:
                return reliability
        
        return SourceReliability.UNKNOWN
    
    # ===== 事実主張抽出・検証 =====
    
    def extract_fact_claims(self, article: ArticleContent) -> List[FactClaim]:
        """記事から事実主張を抽出"""
        claims = []
        content = article.content
        
        # 学名抽出
        scientific_names = self._extract_scientific_names(content)
        for name in scientific_names:
            claims.append(FactClaim(
                claim_id=f"sci_{hashlib.md5(name.encode()).hexdigest()[:8]}",
                text=name,
                fact_type=FactCheckType.SCIENTIFIC_NAME,
                confidence_score=0.9,
                sources=[]
            ))
        
        # 花の特徴抽出
        characteristics = self._extract_flower_characteristics(content)
        for char in characteristics:
            claims.append(FactClaim(
                claim_id=f"char_{hashlib.md5(char.encode()).hexdigest()[:8]}",
                text=char,
                fact_type=FactCheckType.FLOWER_CHARACTERISTICS,
                confidence_score=0.8,
                sources=[]
            ))
        
        # 季節情報抽出
        seasonal_info = self._extract_seasonal_information(content)
        for info in seasonal_info:
            claims.append(FactClaim(
                claim_id=f"seas_{hashlib.md5(info.encode()).hexdigest()[:8]}",
                text=info,
                fact_type=FactCheckType.SEASONAL_INFO,
                confidence_score=0.85,
                sources=[]
            ))
        
        # 育て方情報抽出
        care_instructions = self._extract_care_instructions(content)
        for instruction in care_instructions:
            claims.append(FactClaim(
                claim_id=f"care_{hashlib.md5(instruction.encode()).hexdigest()[:8]}",
                text=instruction,
                fact_type=FactCheckType.CARE_INSTRUCTIONS,
                confidence_score=0.75,
                sources=[]
            ))
        
        return claims
    
    def verify_fact_claims(self, claims: List[FactClaim]) -> List[FactCheckResult]:
        """事実主張の検証"""
        results = []
        
        for claim in claims:
            result = self._verify_single_claim(claim)
            results.append(result)
        
        return results
    
    def _verify_single_claim(self, claim: FactClaim) -> FactCheckResult:
        """単一事実主張の検証"""
        # 知識ベースとの照合
        verified_sources = []
        confidence_score = 0.0
        status = FactCheckStatus.NEEDS_REVIEW
        
        # 事実データベースでの検索
        if claim.fact_type == FactCheckType.SCIENTIFIC_NAME:
            confidence_score, status = self._verify_scientific_name(claim.text)
            if status == FactCheckStatus.VERIFIED:
                verified_sources = ["botanical_database", "scientific_nomenclature"]
        
        elif claim.fact_type == FactCheckType.FLOWER_CHARACTERISTICS:
            confidence_score, status = self._verify_flower_characteristics(claim.text)
            if status == FactCheckStatus.VERIFIED:
                verified_sources = ["flower_database", "horticultural_reference"]
        
        elif claim.fact_type == FactCheckType.SEASONAL_INFO:
            confidence_score, status = self._verify_seasonal_information(claim.text)
            if status == FactCheckStatus.VERIFIED:
                verified_sources = ["seasonal_guide", "gardening_calendar"]
        
        elif claim.fact_type == FactCheckType.CARE_INSTRUCTIONS:
            confidence_score, status = self._verify_care_instructions(claim.text)
            if status == FactCheckStatus.VERIFIED:
                verified_sources = ["gardening_guide", "plant_care_manual"]
        
        return FactCheckResult(
            claim_id=claim.claim_id,
            status=status,
            confidence_score=confidence_score,
            verified_sources=verified_sources
        )
    
    # ===== 誤情報検出 =====
    
    def detect_misinformation(self, article: ArticleContent, fact_check_results: List[FactCheckResult]) -> List[MisinformationAlert]:
        """誤情報検出"""
        alerts = []
        
        # 事実エラーの検出
        for result in fact_check_results:
            if result.status == FactCheckStatus.FACT_ERROR:
                alerts.append(MisinformationAlert(
                    alert_id=f"error_{result.claim_id}",
                    severity="HIGH",
                    claim_text=self._get_claim_text_by_id(result.claim_id),
                    issue_description="事実に反する情報が含まれています",
                    correction_suggestion="正確な情報に修正してください",
                    confidence_score=result.confidence_score
                ))
            
            elif result.status == FactCheckStatus.DISPUTED:
                alerts.append(MisinformationAlert(
                    alert_id=f"disputed_{result.claim_id}",
                    severity="MEDIUM",
                    claim_text=self._get_claim_text_by_id(result.claim_id),
                    issue_description="議論の分かれる情報が含まれています",
                    correction_suggestion="より確実な情報源を参照してください",
                    confidence_score=result.confidence_score
                ))
        
        # 一般的な誤情報パターンの検出
        common_errors = self._detect_common_errors(article.content)
        for error in common_errors:
            alerts.append(error)
        
        return alerts
    
    def _detect_common_errors(self, content: str) -> List[MisinformationAlert]:
        """一般的な誤情報パターン検出"""
        alerts = []
        
        # 矛盾する情報のチェック
        contradictions = self._find_contradictions(content)
        for contradiction in contradictions:
            alerts.append(MisinformationAlert(
                alert_id=f"contradiction_{hashlib.md5(contradiction.encode()).hexdigest()[:8]}",
                severity="MEDIUM",
                claim_text=contradiction,
                issue_description="文章内に矛盾する情報があります",
                confidence_score=0.7
            ))
        
        # 非現実的な主張のチェック
        unrealistic_claims = self._find_unrealistic_claims(content)
        for claim in unrealistic_claims:
            alerts.append(MisinformationAlert(
                alert_id=f"unrealistic_{hashlib.md5(claim.encode()).hexdigest()[:8]}",
                severity="HIGH",
                claim_text=claim,
                issue_description="非現実的または極端な主張が含まれています",
                confidence_score=0.8
            ))
        
        return alerts
    
    # ===== 品質スコア算出 =====
    
    def calculate_quality_score(self, article: ArticleContent, fact_check_results: List[FactCheckResult]) -> float:
        """品質スコア算出"""
        metrics = self._calculate_quality_metrics(article, fact_check_results)
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for metric in metrics:
            total_weighted_score += metric.score * metric.weight
            total_weight += metric.weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_quality_metrics(self, article: ArticleContent, fact_check_results: List[FactCheckResult]) -> List[QualityMetric]:
        """品質メトリック計算"""
        metrics = []
        
        # 事実正確性
        factual_accuracy = self._calculate_factual_accuracy(fact_check_results)
        metrics.append(QualityMetric(
            aspect=QualityAspect.FACTUAL_ACCURACY,
            score=factual_accuracy,
            weight=0.3,
            details={"verified_claims": len([r for r in fact_check_results if r.status == FactCheckStatus.VERIFIED])}
        ))
        
        # 情報源信頼性
        source_reliability = self._calculate_source_reliability(fact_check_results)
        metrics.append(QualityMetric(
            aspect=QualityAspect.SOURCE_RELIABILITY,
            score=source_reliability,
            weight=0.25,
            details={"high_reliability_sources": len([r for r in fact_check_results if r.verified_sources])}
        ))
        
        # コンテンツ完全性
        content_completeness = self._calculate_content_completeness(article)
        metrics.append(QualityMetric(
            aspect=QualityAspect.CONTENT_COMPLETENESS,
            score=content_completeness,
            weight=0.2,
            details={"content_length": len(article.content), "sections_covered": self._count_content_sections(article.content)}
        ))
        
        # 一貫性
        consistency = self._calculate_consistency(article)
        metrics.append(QualityMetric(
            aspect=QualityAspect.CONSISTENCY,
            score=consistency,
            weight=0.15,
            details={"consistent_terminology": True}
        ))
        
        # 読みやすさ
        readability = self._calculate_readability(article.content)
        metrics.append(QualityMetric(
            aspect=QualityAspect.READABILITY,
            score=readability,
            weight=0.1,
            details={"avg_sentence_length": self._calculate_avg_sentence_length(article.content)}
        ))
        
        return metrics
    
    # ===== 最終品質レポート生成 =====
    
    def generate_quality_check_report(self, article: ArticleContent) -> QualityCheckReport:
        """品質チェックレポート生成"""
        # 事実主張抽出
        claims = self.extract_fact_claims(article)
        
        # 事実検証
        fact_check_results = self.verify_fact_claims(claims)
        
        # 誤情報検出
        misinformation_alerts = self.detect_misinformation(article, fact_check_results)
        
        # 品質メトリック計算
        quality_metrics = self._calculate_quality_metrics(article, fact_check_results)
        
        # 総合品質スコア
        overall_score = self.calculate_quality_score(article, fact_check_results)
        
        # 推奨事項生成
        recommendations = self._generate_recommendations(fact_check_results, misinformation_alerts, quality_metrics)
        
        return QualityCheckReport(
            article_id=article.id,
            overall_quality_score=overall_score,
            fact_check_results=fact_check_results,
            quality_metrics=quality_metrics,
            misinformation_alerts=misinformation_alerts,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, fact_results: List[FactCheckResult], alerts: List[MisinformationAlert], metrics: List[QualityMetric]) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # 未検証の主張に対する推奨
        unverified_count = len([r for r in fact_results if r.status == FactCheckStatus.NEEDS_REVIEW])
        if unverified_count > 0:
            recommendations.append(f"{unverified_count}件の未検証情報について追加の確認が必要です")
        
        # 高重要度アラートに対する推奨
        high_severity_alerts = len([a for a in alerts if a.severity == "HIGH"])
        if high_severity_alerts > 0:
            recommendations.append(f"{high_severity_alerts}件の重要な問題を修正してください")
        
        # 品質メトリックに基づく推奨
        for metric in metrics:
            if metric.score < 0.7:
                recommendations.append(f"{metric.aspect.value}の改善が推奨されます（現在: {metric.score:.2f}）")
        
        return recommendations
    
    # ===== プライベートメソッド =====
    
    def _extract_scientific_names(self, content: str) -> List[str]:
        """学名抽出"""
        # 学名パターン（斜体、括弧内など）
        patterns = [
            r'[A-Z][a-z]+ [a-z]+',  # 基本的な学名パターン
            r'\([A-Z][a-z]+ [a-z]+\)',  # 括弧内の学名
        ]
        
        scientific_names = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            scientific_names.extend(matches)
        
        return list(set(scientific_names))
    
    def _extract_flower_characteristics(self, content: str) -> List[str]:
        """花の特徴抽出"""
        characteristics = []
        
        # 色に関する記述
        color_patterns = [
            r'[白赤青黄ピンク紫橙緑][色い]',
            r'[白赤青黄ピンク紫橙緑]い花',
        ]
        
        for pattern in color_patterns:
            matches = re.findall(pattern, content)
            characteristics.extend(matches)
        
        # サイズに関する記述
        size_patterns = [
            r'[大小中]きな花',
            r'[高低]さ\d+[cm]+',
        ]
        
        for pattern in size_patterns:
            matches = re.findall(pattern, content)
            characteristics.extend(matches)
        
        return list(set(characteristics))
    
    def _extract_seasonal_information(self, content: str) -> List[str]:
        """季節情報抽出"""
        seasonal_info = []
        
        # 開花時期
        season_patterns = [
            r'[1-9][0-2]?月[に〜から]?咲く',
            r'[春夏秋冬][に〜から]?咲く',
            r'[1-9][0-2]?月[の〜から][1-9][0-2]?月',
        ]
        
        for pattern in season_patterns:
            matches = re.findall(pattern, content)
            seasonal_info.extend(matches)
        
        return list(set(seasonal_info))
    
    def _extract_care_instructions(self, content: str) -> List[str]:
        """育て方情報抽出"""
        care_info = []
        
        # 水やり、日光、土壌に関する記述
        care_patterns = [
            r'水[やり〜を][^。]*',
            r'日光[が〜を][^。]*',
            r'土[が〜を][^。]*',
            r'肥料[が〜を][^。]*',
        ]
        
        for pattern in care_patterns:
            matches = re.findall(pattern, content)
            care_info.extend(matches)
        
        return list(set(care_info))
    
    def _verify_scientific_name(self, name: str) -> Tuple[float, FactCheckStatus]:
        """学名検証"""
        # 簡易的な学名検証（実際の実装では植物データベースと照合）
        known_names = {
            "Rosa gallica": 0.95,
            "Tulipa gesneriana": 0.9,
            "Prunus serrulata": 0.9,
            "Primula vulgaris": 0.85,
        }
        
        if name in known_names:
            return known_names[name], FactCheckStatus.VERIFIED
        
        # 学名の形式チェック
        if re.match(r'^[A-Z][a-z]+ [a-z]+$', name):
            return 0.7, FactCheckStatus.NEEDS_REVIEW
        
        return 0.3, FactCheckStatus.DISPUTED
    
    def _verify_flower_characteristics(self, characteristic: str) -> Tuple[float, FactCheckStatus]:
        """花の特徴検証"""
        # 一般的な花の特徴の検証
        common_characteristics = [
            "白い花", "赤い花", "ピンクの花", "小さな花", "大きな花"
        ]
        
        if any(char in characteristic for char in common_characteristics):
            return 0.8, FactCheckStatus.VERIFIED
        
        return 0.6, FactCheckStatus.NEEDS_REVIEW
    
    def _verify_seasonal_information(self, info: str) -> Tuple[float, FactCheckStatus]:
        """季節情報検証"""
        # 季節情報の妥当性チェック
        if any(month in info for month in ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]):
            return 0.85, FactCheckStatus.VERIFIED
        
        if any(season in info for season in ["春", "夏", "秋", "冬"]):
            return 0.8, FactCheckStatus.VERIFIED
        
        return 0.5, FactCheckStatus.NEEDS_REVIEW
    
    def _verify_care_instructions(self, instruction: str) -> Tuple[float, FactCheckStatus]:
        """育て方指示検証"""
        # 一般的な植物ケア指示の検証
        valid_instructions = ["水やり", "日光", "土", "肥料", "剪定", "植え替え"]
        
        if any(inst in instruction for inst in valid_instructions):
            return 0.75, FactCheckStatus.VERIFIED
        
        return 0.5, FactCheckStatus.NEEDS_REVIEW
    
    def _get_claim_text_by_id(self, claim_id: str) -> str:
        """クレームIDからテキストを取得"""
        # 実装簡略化のため固定値を返す
        return f"主張内容 (ID: {claim_id})"
    
    def _find_contradictions(self, content: str) -> List[str]:
        """矛盾検出"""
        contradictions = []
        
        # 簡易的な矛盾検出例
        if "簡単" in content and "難しい" in content:
            contradictions.append("育成の難易度について矛盾する記述があります")
        
        if "年中" in content and any(season in content for season in ["春のみ", "夏のみ", "秋のみ", "冬のみ"]):
            contradictions.append("開花時期について矛盾する記述があります")
        
        return contradictions
    
    def _find_unrealistic_claims(self, content: str) -> List[str]:
        """非現実的な主張検出"""
        unrealistic = []
        
        # 極端な表現の検出
        extreme_patterns = [
            r'絶対に[^。]*',
            r'100%[^。]*',
            r'完璧[^。]*',
        ]
        
        for pattern in extreme_patterns:
            matches = re.findall(pattern, content)
            if matches:
                unrealistic.extend(matches)
        
        return unrealistic
    
    def _calculate_factual_accuracy(self, results: List[FactCheckResult]) -> float:
        """事実正確性計算"""
        if not results:
            return 0.8
        
        verified_count = len([r for r in results if r.status == FactCheckStatus.VERIFIED])
        total_count = len(results)
        
        return verified_count / total_count
    
    def _calculate_source_reliability(self, results: List[FactCheckResult]) -> float:
        """情報源信頼性計算"""
        if not results:
            return 0.7
        
        reliable_count = len([r for r in results if r.verified_sources])
        total_count = len(results)
        
        return reliable_count / total_count
    
    def _calculate_content_completeness(self, article: ArticleContent) -> float:
        """コンテンツ完全性計算"""
        required_sections = ["特徴", "育て方", "花言葉"]
        covered_sections = sum(1 for section in required_sections if section in article.content)
        
        length_score = min(len(article.content) / 300, 1.0)  # 300文字を基準
        section_score = covered_sections / len(required_sections)
        
        return (length_score + section_score) / 2
    
    def _calculate_consistency(self, article: ArticleContent) -> float:
        """一貫性計算"""
        # 簡易的な一貫性チェック
        content = article.content
        
        # 同じ花の名前が一貫して使われているかチェック
        flower_names = re.findall(r'[ァ-ヶ]+', content)  # カタカナの花名
        if flower_names:
            most_common = Counter(flower_names).most_common(1)[0]
            consistency_ratio = most_common[1] / len(flower_names)
            return consistency_ratio
        
        return 0.8
    
    def _calculate_readability(self, content: str) -> float:
        """読みやすさ計算"""
        sentences = re.split(r'[。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        avg_length = statistics.mean([len(sentence) for sentence in sentences])
        
        # 理想的な文長を50文字とする
        ideal_length = 50
        readability = 1.0 - abs(avg_length - ideal_length) / ideal_length
        
        return max(0.0, min(1.0, readability))
    
    def _count_content_sections(self, content: str) -> int:
        """コンテンツセクション数カウント"""
        sections = ["特徴", "育て方", "花言葉", "由来", "季節"]
        return sum(1 for section in sections if section in content)
    
    def _calculate_avg_sentence_length(self, content: str) -> float:
        """平均文長計算"""
        sentences = re.split(r'[。！？]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        return statistics.mean([len(sentence) for sentence in sentences])
    
    def _initialize_trusted_sources(self):
        """信頼できる情報源初期化"""
        sources = [
            TrustedSource(
                source_id="botanical_jp",
                name="日本植物学会",
                url="https://botanical.jp",
                reliability_level=SourceReliability.HIGH,
                expertise_areas=["植物学", "分類学", "生態学"],
                verification_date=datetime.now()
            ),
            TrustedSource(
                source_id="flower_garden_guide",
                name="ガーデニング総合ガイド",
                url="https://garden-guide.jp",
                reliability_level=SourceReliability.MEDIUM,
                expertise_areas=["園芸", "栽培", "花卉"],
                verification_date=datetime.now()
            ),
        ]
        
        for source in sources:
            self.add_trusted_source(source)
    
    def _initialize_verification_patterns(self):
        """検証パターン初期化"""
        self.verification_patterns = {
            "scientific_names": [
                r"^[A-Z][a-z]+ [a-z]+$",  # 標準的な学名形式
                r"^[A-Z][a-z]+ [a-z]+ [a-z]+$",  # 亜種を含む学名
            ],
            "seasonal_info": [
                r"[1-9][0-2]?月",  # 月の記述
                r"[春夏秋冬]",      # 季節の記述
            ],
        }
    
    def _initialize_flower_facts_database(self):
        """花の事実データベース初期化"""
        # 誕生花の基本データベース
        birth_flowers = {
            "1月": ["カーネーション", "スノードロップ", "ガーベラ"],
            "2月": ["プリムラ", "フリージア", "マーガレット"],
            "3月": ["桜", "スイートピー", "チューリップ"],
            "4月": ["桜草", "カスミソウ", "アルストロメリア"],
        }
        
        for month, flowers in birth_flowers.items():
            for flower in flowers:
                self.fact_database[f"birth_flower_{month}"].append(
                    FactClaim(
                        claim_id=f"birth_{month}_{flower}",
                        text=f"{flower}は{month}の誕生花",
                        fact_type=FactCheckType.SEASONAL_INFO,
                        confidence_score=0.9,
                        sources=["birth_flower_calendar", "traditional_references"]
                    )
                )


# エクスポート
__all__ = [
    'FactCheckingSystem',
    'QualityCheckReport',
    'FactCheckResult',
    'MisinformationAlert',
    'QualityMetric',
    'TrustedSource',
    'FactClaim',
    'FactCheckStatus',
    'SourceReliability',
    'QualityAspect'
]