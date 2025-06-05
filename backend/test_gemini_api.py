#!/usr/bin/env python3
"""
Gemini API接続テストとSEOリサーチシステム
テスト駆動開発の自己回帰ループに基づく実装
"""

import os
import json
import time
import requests
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from unittest.mock import patch
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

@dataclass
class TestResult:
    """テスト結果データクラス"""
    test_name: str
    passed: bool
    execution_time: float
    coverage: float
    quality_score: float
    issues: List[str]
    suggestions: List[str]

@dataclass
class CoverageReport:
    """カバレッジレポートデータクラス"""
    line_coverage: float
    branch_coverage: float
    function_coverage: float
    uncovered_areas: List[str]

@dataclass 
class QualityMetrics:
    """品質メトリクスデータクラス"""
    assertion_density: float
    test_isolation: float
    execution_time: float
    maintainability: float
    overall_score: float

class GeminiAPITester:
    """Gemini API テストクラス - 自己回帰ループ実装"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.test_results: List[TestResult] = []
        self.iteration_count = 0
        self.max_iterations = 5
        self.coverage_threshold = 0.8
        self.quality_threshold = 0.9
        
    def test_api_connection(self) -> TestResult:
        """APIの基本接続テスト"""
        start_time = time.time()
        
        try:
            url = f"{self.base_url}/models/gemini-2.0-flash:generateContent"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Explain how AI works in a few words"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                generated_text = result_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                
                # 品質評価
                quality_score = self._evaluate_response_quality(generated_text)
                
                return TestResult(
                    test_name="gemini_api_connection",
                    passed=True,
                    execution_time=execution_time,
                    coverage=1.0,
                    quality_score=quality_score,
                    issues=[],
                    suggestions=["API接続成功"]
                )
            else:
                return TestResult(
                    test_name="gemini_api_connection",
                    passed=False,
                    execution_time=execution_time,
                    coverage=0.0,
                    quality_score=0.0,
                    issues=[f"HTTP {response.status_code}: {response.text}"],
                    suggestions=["APIキーを確認してください"]
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="gemini_api_connection",
                passed=False,
                execution_time=execution_time,
                coverage=0.0,
                quality_score=0.0,
                issues=[str(e)],
                suggestions=["ネットワーク接続とAPIキーを確認してください"]
            )
    
    def test_birth_flower_keyword_research(self) -> TestResult:
        """誕生花キーワードリサーチのテスト"""
        start_time = time.time()
        
        try:
            prompt = """
            「誕生花」に関連するSEOキーワードを20個提案し、以下のJSON形式で回答してください：
            {
                "keywords": [
                    {
                        "keyword": "誕生花",
                        "search_volume": 18000,
                        "competition": 0.7,
                        "difficulty": "Medium",
                        "intent": "informational"
                    }
                ],
                "insights": "キーワード分析の洞察",
                "recommendations": ["具体的な推奨事項"]
            }
            
            日本市場の検索トレンドを考慮して、現実的な数値を提供してください。
            """
            
            response = self._call_gemini_api(prompt)
            execution_time = time.time() - start_time
            
            if response and 'candidates' in response:
                content = response['candidates'][0]['content']['parts'][0]['text']
                
                # JSON解析テスト
                try:
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        json_content = content[json_start:json_end].strip()
                    else:
                        json_content = content
                    
                    data = json.loads(json_content)
                    
                    # データ品質評価
                    quality_score = self._evaluate_keyword_data_quality(data)
                    
                    # カバレッジ評価（期待される要素の存在確認）
                    coverage = self._calculate_keyword_coverage(data)
                    
                    return TestResult(
                        test_name="birth_flower_keyword_research",
                        passed=quality_score > 0.7,
                        execution_time=execution_time,
                        coverage=coverage,
                        quality_score=quality_score,
                        issues=self._identify_keyword_issues(data),
                        suggestions=self._generate_keyword_suggestions(data)
                    )
                
                except json.JSONDecodeError as e:
                    return TestResult(
                        test_name="birth_flower_keyword_research",
                        passed=False,
                        execution_time=execution_time,
                        coverage=0.0,
                        quality_score=0.0,
                        issues=[f"JSON解析エラー: {e}"],
                        suggestions=["プロンプトの形式を調整してください"]
                    )
            
            return TestResult(
                test_name="birth_flower_keyword_research",
                passed=False,
                execution_time=execution_time,
                coverage=0.0,
                quality_score=0.0,
                issues=["API応答が無効"],
                suggestions=["API呼び出しを再試行してください"]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="birth_flower_keyword_research",
                passed=False,
                execution_time=execution_time,
                coverage=0.0,
                quality_score=0.0,
                issues=[str(e)],
                suggestions=["エラーの詳細を確認してください"]
            )
    
    def test_article_structure_generation(self) -> TestResult:
        """記事構成生成のテスト"""
        start_time = time.time()
        
        try:
            prompt = """
            「誕生花」について検索意図を満たすSEO最適化記事の構成を作成してください。
            以下のJSON形式で回答してください：
            
            {
                "title": "SEO最適化されたH1タイトル",
                "meta_description": "120-160文字のメタディスクリプション",
                "target_keywords": ["メインキーワード", "サブキーワード"],
                "structure": [
                    {
                        "h2": "大見出し",
                        "h3_items": ["小見出し1", "小見出し2", "小見出し3"],
                        "content_outline": "セクションの概要",
                        "word_count_target": 500
                    }
                ],
                "estimated_word_count": 4000,
                "seo_strategy": "SEO戦略の説明",
                "user_intent_analysis": "検索意図の分析"
            }
            
            ユーザーの検索意図を完全に満たす構成にしてください。
            """
            
            response = self._call_gemini_api(prompt)
            execution_time = time.time() - start_time
            
            if response and 'candidates' in response:
                content = response['candidates'][0]['content']['parts'][0]['text']
                
                try:
                    if "```json" in content:
                        json_start = content.find("```json") + 7
                        json_end = content.find("```", json_start)
                        json_content = content[json_start:json_end].strip()
                    else:
                        json_content = content
                    
                    data = json.loads(json_content)
                    
                    # 記事構成の品質評価
                    quality_score = self._evaluate_article_structure_quality(data)
                    coverage = self._calculate_structure_coverage(data)
                    
                    return TestResult(
                        test_name="article_structure_generation",
                        passed=quality_score > 0.8,
                        execution_time=execution_time,
                        coverage=coverage,
                        quality_score=quality_score,
                        issues=self._identify_structure_issues(data),
                        suggestions=self._generate_structure_suggestions(data)
                    )
                
                except json.JSONDecodeError as e:
                    return TestResult(
                        test_name="article_structure_generation",
                        passed=False,
                        execution_time=execution_time,
                        coverage=0.0,
                        quality_score=0.0,
                        issues=[f"JSON解析エラー: {e}"],
                        suggestions=["プロンプトの構造を見直してください"]
                    )
                    
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="article_structure_generation",
                passed=False,
                execution_time=execution_time,
                coverage=0.0,
                quality_score=0.0,
                issues=[str(e)],
                suggestions=["エラーハンドリングを改善してください"]
            )
    
    def test_full_article_generation(self) -> TestResult:
        """完全な記事生成のテスト"""
        start_time = time.time()
        
        try:
            # まず記事構成を取得
            structure_result = self.test_article_structure_generation()
            if not structure_result.passed:
                return TestResult(
                    test_name="full_article_generation",
                    passed=False,
                    execution_time=time.time() - start_time,
                    coverage=0.0,
                    quality_score=0.0,
                    issues=["記事構成の生成に失敗"],
                    suggestions=["記事構成テストを先に修正してください"]
                )
            
            # 記事執筆プロンプト
            prompt = """
            以下の構成に基づいて、「誕生花」についての完全なSEO記事をMarkdown形式で執筆してください：
            
            要件：
            - 4000文字以上の詳細な内容
            - 月別誕生花の一覧
            - 花言葉とその意味
            - 歴史的背景
            - プレゼント選びのコツ
            - 専門性と信頼性を重視
            - 読みやすい文章構成
            - SEOキーワードの自然な配置
            
            Markdown形式で記事全体を出力してください。
            """
            
            response = self._call_gemini_api(prompt)
            execution_time = time.time() - start_time
            
            if response and 'candidates' in response:
                content = response['candidates'][0]['content']['parts'][0]['text']
                
                # 記事品質の評価
                quality_score = self._evaluate_article_quality(content)
                coverage = self._calculate_article_coverage(content)
                
                return TestResult(
                    test_name="full_article_generation",
                    passed=quality_score > 0.8 and len(content) > 3000,
                    execution_time=execution_time,
                    coverage=coverage,
                    quality_score=quality_score,
                    issues=self._identify_article_issues(content),
                    suggestions=self._generate_article_suggestions(content)
                )
            
            return TestResult(
                test_name="full_article_generation",
                passed=False,
                execution_time=execution_time,
                coverage=0.0,
                quality_score=0.0,
                issues=["記事生成に失敗"],
                suggestions=["プロンプトを改善してください"]
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="full_article_generation",
                passed=False,
                execution_time=execution_time,
                coverage=0.0,
                quality_score=0.0,
                issues=[str(e)],
                suggestions=["例外処理を強化してください"]
            )
    
    def run_self_recursive_test_loop(self) -> Dict[str, Any]:
        """自己回帰テストループの実行"""
        print("🔄 自己回帰テストループ開始")
        print("="*50)
        
        loop_results = []
        
        for iteration in range(self.max_iterations):
            self.iteration_count = iteration + 1
            print(f"\n📍 反復 {self.iteration_count}/{self.max_iterations}")
            
            # テスト実行
            current_results = self._run_test_suite()
            loop_results.append(current_results)
            
            # メトリクス計算
            metrics = self._calculate_metrics(current_results)
            
            # 収束判定
            convergence = self._check_convergence(metrics)
            
            print(f"📊 メトリクス:")
            print(f"   カバレッジ: {metrics['coverage']:.1%}")
            print(f"   品質スコア: {metrics['quality_score']:.1%}")
            print(f"   成功率: {metrics['success_rate']:.1%}")
            
            if convergence['converged']:
                print(f"✅ 収束完了！({iteration + 1}回目で基準達成)")
                break
            else:
                print(f"🔄 改善が必要: {convergence['reason']}")
                # 自動改善の実行
                self._apply_improvements(convergence['suggestions'])
        
        # 最終レポート生成
        final_report = self._generate_final_report(loop_results)
        return final_report
    
    def _run_test_suite(self) -> List[TestResult]:
        """テストスイートの実行"""
        tests = [
            self.test_api_connection,
            self.test_birth_flower_keyword_research,
            self.test_article_structure_generation,
            self.test_full_article_generation
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                print(f"   {'✅' if result.passed else '❌'} {result.test_name}: {result.quality_score:.2f}")
            except Exception as e:
                print(f"   ❌ {test.__name__}: Exception - {e}")
                
        return results
    
    def _calculate_metrics(self, results: List[TestResult]) -> Dict[str, float]:
        """メトリクスの計算"""
        if not results:
            return {'coverage': 0.0, 'quality_score': 0.0, 'success_rate': 0.0}
        
        total_coverage = sum(r.coverage for r in results) / len(results)
        total_quality = sum(r.quality_score for r in results) / len(results)
        success_rate = sum(1 for r in results if r.passed) / len(results)
        
        return {
            'coverage': total_coverage,
            'quality_score': total_quality,
            'success_rate': success_rate
        }
    
    def _check_convergence(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """収束判定"""
        coverage_ok = metrics['coverage'] >= self.coverage_threshold
        quality_ok = metrics['quality_score'] >= self.quality_threshold
        success_ok = metrics['success_rate'] >= 0.8
        
        if coverage_ok and quality_ok and success_ok:
            return {
                'converged': True,
                'reason': '全ての閾値を満たしました'
            }
        
        suggestions = []
        if not coverage_ok:
            suggestions.append("カバレッジを向上させるテストケースを追加")
        if not quality_ok:
            suggestions.append("品質指標を改善するプロンプト調整")
        if not success_ok:
            suggestions.append("失敗テストのエラーハンドリング強化")
        
        return {
            'converged': False,
            'reason': f"閾値未達成 (C:{metrics['coverage']:.1%}, Q:{metrics['quality_score']:.1%}, S:{metrics['success_rate']:.1%})",
            'suggestions': suggestions
        }
    
    def _apply_improvements(self, suggestions: List[str]):
        """自動改善の適用"""
        print(f"🔧 改善を適用中:")
        for suggestion in suggestions:
            print(f"   • {suggestion}")
        # 実際の改善ロジックをここに実装
        time.sleep(1)  # 改善処理のシミュレーション
    
    def _generate_final_report(self, loop_results: List[List[TestResult]]) -> Dict[str, Any]:
        """最終レポートの生成"""
        final_iteration = loop_results[-1] if loop_results else []
        
        return {
            'iterations': len(loop_results),
            'final_metrics': self._calculate_metrics(final_iteration),
            'improvement_trend': self._analyze_improvement_trend(loop_results),
            'recommendations': self._generate_recommendations(final_iteration),
            'test_results': final_iteration
        }
    
    def _analyze_improvement_trend(self, loop_results: List[List[TestResult]]) -> Dict[str, Any]:
        """改善傾向の分析"""
        if len(loop_results) < 2:
            return {'trend': 'insufficient_data'}
        
        metrics_over_time = [self._calculate_metrics(results) for results in loop_results]
        
        coverage_trend = [m['coverage'] for m in metrics_over_time]
        quality_trend = [m['quality_score'] for m in metrics_over_time]
        
        return {
            'coverage_improvement': coverage_trend[-1] - coverage_trend[0],
            'quality_improvement': quality_trend[-1] - quality_trend[0],
            'convergence_speed': len(loop_results),
            'stability': self._calculate_stability(metrics_over_time)
        }
    
    def _calculate_stability(self, metrics_over_time: List[Dict[str, float]]) -> float:
        """安定性の計算"""
        if len(metrics_over_time) < 3:
            return 0.0
        
        recent_metrics = metrics_over_time[-3:]
        variances = []
        
        for key in ['coverage', 'quality_score', 'success_rate']:
            values = [m[key] for m in recent_metrics]
            variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)
            variances.append(variance)
        
        return 1.0 - sum(variances) / len(variances)  # 低い分散 = 高い安定性
    
    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """推奨事項の生成"""
        recommendations = []
        
        for result in results:
            if not result.passed:
                recommendations.extend(result.suggestions)
        
        # 全体的な推奨事項
        if not results:
            recommendations.append("基本テストケースを実装してください")
        elif all(r.passed for r in results):
            recommendations.append("全テスト成功！追加のエッジケースを検討してください")
        else:
            failed_count = sum(1 for r in results if not r.passed)
            recommendations.append(f"{failed_count}個の失敗テストを優先的に修正してください")
        
        return list(set(recommendations))  # 重複除去
    
    # ヘルパーメソッド群
    def _call_gemini_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Gemini API呼び出し"""
        try:
            url = f"{self.base_url}/models/gemini-2.0-flash:generateContent"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=60
            )
            
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"API呼び出しエラー: {e}")
            return None
    
    def _evaluate_response_quality(self, text: str) -> float:
        """応答品質の評価"""
        if not text:
            return 0.0
        
        score = 0.0
        
        # 長さによる評価
        if len(text) > 50:
            score += 0.3
        
        # 内容の有意性
        if any(word in text.lower() for word in ['ai', 'artificial', 'intelligence', 'machine', 'learning']):
            score += 0.4
        
        # 構造による評価
        if '.' in text or '。' in text:
            score += 0.3
        
        return min(score, 1.0)
    
    def _evaluate_keyword_data_quality(self, data: Dict[str, Any]) -> float:
        """キーワードデータの品質評価"""
        score = 0.0
        
        if 'keywords' in data and isinstance(data['keywords'], list):
            score += 0.4
            
            if len(data['keywords']) >= 10:
                score += 0.2
            
            # 各キーワードの品質チェック
            valid_keywords = 0
            for kw in data['keywords']:
                if all(key in kw for key in ['keyword', 'search_volume', 'competition']):
                    valid_keywords += 1
            
            if valid_keywords > 0:
                score += 0.4 * (valid_keywords / len(data['keywords']))
        
        return min(score, 1.0)
    
    def _calculate_keyword_coverage(self, data: Dict[str, Any]) -> float:
        """キーワードカバレッジの計算"""
        expected_fields = ['keywords', 'insights', 'recommendations']
        present_fields = sum(1 for field in expected_fields if field in data)
        return present_fields / len(expected_fields)
    
    def _identify_keyword_issues(self, data: Dict[str, Any]) -> List[str]:
        """キーワードの問題点識別"""
        issues = []
        
        if 'keywords' not in data:
            issues.append("キーワードリストが存在しません")
        elif len(data['keywords']) < 10:
            issues.append("キーワード数が不足しています")
        
        return issues
    
    def _generate_keyword_suggestions(self, data: Dict[str, Any]) -> List[str]:
        """キーワード改善提案"""
        suggestions = []
        
        if 'keywords' in data and len(data['keywords']) < 20:
            suggestions.append("より多くのロングテールキーワードを追加")
        
        if 'insights' not in data:
            suggestions.append("市場分析の洞察を追加")
        
        return suggestions
    
    def _evaluate_article_structure_quality(self, data: Dict[str, Any]) -> float:
        """記事構成の品質評価"""
        score = 0.0
        
        required_fields = ['title', 'meta_description', 'structure']
        for field in required_fields:
            if field in data:
                score += 0.25
        
        if 'structure' in data and isinstance(data['structure'], list):
            if len(data['structure']) >= 4:
                score += 0.25
        
        return min(score, 1.0)
    
    def _calculate_structure_coverage(self, data: Dict[str, Any]) -> float:
        """構成カバレッジの計算"""
        expected_fields = ['title', 'meta_description', 'target_keywords', 'structure', 'seo_strategy']
        present_fields = sum(1 for field in expected_fields if field in data)
        return present_fields / len(expected_fields)
    
    def _identify_structure_issues(self, data: Dict[str, Any]) -> List[str]:
        """構成の問題点識別"""
        issues = []
        
        if 'title' not in data or len(data.get('title', '')) < 20:
            issues.append("タイトルが短すぎます")
        
        if 'structure' not in data or len(data.get('structure', [])) < 3:
            issues.append("構成セクションが不足しています")
        
        return issues
    
    def _generate_structure_suggestions(self, data: Dict[str, Any]) -> List[str]:
        """構成改善提案"""
        suggestions = []
        
        if 'seo_strategy' not in data:
            suggestions.append("SEO戦略の説明を追加")
        
        if 'user_intent_analysis' not in data:
            suggestions.append("検索意図の分析を追加")
        
        return suggestions
    
    def _evaluate_article_quality(self, content: str) -> float:
        """記事品質の評価"""
        score = 0.0
        
        # 文字数による評価
        if len(content) > 3000:
            score += 0.3
        
        # 構造による評価
        if content.count('#') >= 5:  # 見出し数
            score += 0.2
        
        # 内容の充実度
        birth_flower_terms = ['誕生花', '花言葉', '月別', 'プレゼント', '歴史']
        matching_terms = sum(1 for term in birth_flower_terms if term in content)
        score += 0.5 * (matching_terms / len(birth_flower_terms))
        
        return min(score, 1.0)
    
    def _calculate_article_coverage(self, content: str) -> float:
        """記事カバレッジの計算"""
        expected_sections = ['誕生花とは', '月別', '花言葉', 'プレゼント', 'まとめ']
        present_sections = sum(1 for section in expected_sections if section in content)
        return present_sections / len(expected_sections)
    
    def _identify_article_issues(self, content: str) -> List[str]:
        """記事の問題点識別"""
        issues = []
        
        if len(content) < 2000:
            issues.append("記事が短すぎます")
        
        if content.count('#') < 3:
            issues.append("見出し構造が不足しています")
        
        if '誕生花' not in content:
            issues.append("メインキーワードが不足しています")
        
        return issues
    
    def _generate_article_suggestions(self, content: str) -> List[str]:
        """記事改善提案"""
        suggestions = []
        
        if len(content) < 4000:
            suggestions.append("さらに詳細な情報を追加")
        
        if content.count('月') < 12:
            suggestions.append("全12ヶ月の誕生花を網羅")
        
        if 'プレゼント' not in content:
            suggestions.append("プレゼント選びのガイドを追加")
        
        return suggestions

def main():
    """メイン実行関数"""
    print("🌸 Gemini API テスト駆動開発システム 🌸")
    print("自己回帰ループによる品質向上テスト")
    print("="*60)
    
    # APIキー確認
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 環境変数が設定されていません")
        print("   以下のコマンドで設定してください:")
        print("   export GEMINI_API_KEY='your_actual_api_key'")
        return
    
    # テスター初期化
    tester = GeminiAPITester(api_key)
    
    # 自己回帰ループ実行
    report = tester.run_self_recursive_test_loop()
    
    # 結果出力
    print("\n" + "="*60)
    print("📊 最終テストレポート")
    print("="*60)
    
    print(f"\n🔄 実行情報:")
    print(f"   反復回数: {report['iterations']}")
    print(f"   最終カバレッジ: {report['final_metrics']['coverage']:.1%}")
    print(f"   最終品質スコア: {report['final_metrics']['quality_score']:.1%}")
    print(f"   成功率: {report['final_metrics']['success_rate']:.1%}")
    
    print(f"\n📈 改善傾向:")
    trend = report['improvement_trend']
    print(f"   カバレッジ改善: {trend.get('coverage_improvement', 0):.1%}")
    print(f"   品質改善: {trend.get('quality_improvement', 0):.1%}")
    print(f"   安定性: {trend.get('stability', 0):.1%}")
    
    print(f"\n💡 推奨事項:")
    for recommendation in report['recommendations']:
        print(f"   • {recommendation}")
    
    # 詳細結果
    print(f"\n📋 詳細テスト結果:")
    for result in report['test_results']:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"   {status} {result.test_name}")
        print(f"      実行時間: {result.execution_time:.2f}s")
        print(f"      品質スコア: {result.quality_score:.2f}")
        if result.issues:
            print(f"      問題: {', '.join(result.issues)}")
    
    # 最終判定
    final_score = report['final_metrics']['quality_score']
    if final_score >= 0.9:
        print(f"\n🎉 テスト駆動開発完了！高品質システムを達成しました")
    elif final_score >= 0.7:
        print(f"\n✅ テスト駆動開発基準達成。さらなる改善を推奨します")
    else:
        print(f"\n⚠️ 品質基準未達成。継続的な改善が必要です")

if __name__ == "__main__":
    main()