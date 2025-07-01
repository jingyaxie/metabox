import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Settings, TestTube, BarChart3, Filter, Search } from 'lucide-react';
import api from '../services/api';

interface PipelineConfig {
  enable_query_preprocessing: boolean;
  enable_query_expansion: boolean;
  expansion_strategy: string;
  expansion_count: number;
  enable_metadata_filtering: boolean;
  predefined_filters: string[];
  enable_hybrid_retrieval: boolean;
  fusion_strategy: string;
  retrieval_weights: { [key: string]: number };
  enable_reranking: boolean;
  rerank_strategy: string;
  rerank_top_k: number;
  max_retrieval_results: number;
  final_top_k: number;
  enable_parallel_processing: boolean;
}

interface PipelineStats {
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  avg_processing_time: number;
  stage_performance: { [key: string]: any };
}

const EnhancedRetrievalPanel: React.FC = () => {
  const [config, setConfig] = useState<PipelineConfig | null>(null);
  const [stats, setStats] = useState<PipelineStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState<any>(null);
  const [availableFilters, setAvailableFilters] = useState<string[]>([]);
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [error, setError] = useState<string>('');

  // 加载配置和统计信息
  useEffect(() => {
    loadConfig();
    loadStats();
    loadAvailableFilters();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await api.get('/enhanced-retrieval/config');
      if (response.data.success) {
        setConfig(response.data.data);
      }
    } catch (err) {
      console.error('加载配置失败:', err);
      setError('加载配置失败');
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/enhanced-retrieval/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (err) {
      console.error('加载统计信息失败:', err);
    }
  };

  const loadAvailableFilters = async () => {
    try {
      const response = await api.get('/enhanced-retrieval/available-filters');
      if (response.data.success) {
        setAvailableFilters(response.data.data.available_filters);
      }
    } catch (err) {
      console.error('加载可用过滤器失败:', err);
    }
  };

  const updateConfig = async (newConfig: Partial<PipelineConfig>) => {
    try {
      setLoading(true);
      const response = await api.post('/enhanced-retrieval/config', {
        ...config,
        ...newConfig
      });
      if (response.data.success) {
        setConfig(response.data.data.config);
        setError('');
      }
    } catch (err) {
      console.error('更新配置失败:', err);
      setError('更新配置失败');
    } finally {
      setLoading(false);
    }
  };

  const testQueryExpansion = async () => {
    if (!testQuery.trim()) return;

    try {
      setLoading(true);
      const response = await api.post('/enhanced-retrieval/test-query-expansion', null, {
        params: {
          query: testQuery,
          strategy: config?.expansion_strategy || 'hybrid',
          expansion_count: config?.expansion_count || 3
        }
      });
      if (response.data.success) {
        setTestResults(response.data.data);
        setError('');
      }
    } catch (err) {
      console.error('测试查询扩展失败:', err);
      setError('测试查询扩展失败');
    } finally {
      setLoading(false);
    }
  };

  const testMetadataFiltering = async () => {
    // 模拟文档数据用于测试
    const testDocuments = [
      {
        id: '1',
        content: '这是一个包含代码的文档 ```python print("hello") ```',
        metadata: {
          source_type: 'official_doc',
          quality_score: 0.8,
          created_at: '2024-01-01T00:00:00Z'
        }
      },
      {
        id: '2',
        content: '这是一个普通文档',
        metadata: {
          source_type: 'blog',
          quality_score: 0.6,
          created_at: '2024-01-15T00:00:00Z'
        }
      }
    ];

    try {
      setLoading(true);
      const response = await api.post('/enhanced-retrieval/test-metadata-filtering', testDocuments, {
        params: {
          predefined_filters: selectedFilters
        }
      });
      if (response.data.success) {
        setTestResults(response.data.data);
        setError('');
      }
    } catch (err) {
      console.error('测试元数据过滤失败:', err);
      setError('测试元数据过滤失败');
    } finally {
      setLoading(false);
    }
  };

  const toggleFilter = (filter: string) => {
    setSelectedFilters(prev => 
      prev.includes(filter) 
        ? prev.filter(f => f !== filter)
        : [...prev, filter]
    );
  };

  if (!config) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">增强检索配置</h2>
        <Button onClick={loadStats} variant="outline" size="sm">
          <BarChart3 className="h-4 w-4 mr-2" />
          刷新统计
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="config" className="space-y-4">
        <TabsList>
          <TabsTrigger value="config">
            <Settings className="h-4 w-4 mr-2" />
            配置
          </TabsTrigger>
          <TabsTrigger value="test">
            <TestTube className="h-4 w-4 mr-2" />
            测试
          </TabsTrigger>
          <TabsTrigger value="stats">
            <BarChart3 className="h-4 w-4 mr-2" />
            统计
          </TabsTrigger>
        </TabsList>

        <TabsContent value="config" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 查询预处理配置 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Search className="h-5 w-5 mr-2" />
                  查询预处理
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="query-preprocessing">启用查询预处理</Label>
                  <Switch
                    id="query-preprocessing"
                    checked={config.enable_query_preprocessing}
                    onCheckedChange={(checked) => 
                      updateConfig({ enable_query_preprocessing: checked })
                    }
                  />
                </div>
              </CardContent>
            </Card>

            {/* 查询扩展配置 */}
            <Card>
              <CardHeader>
                <CardTitle>查询扩展</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="query-expansion">启用查询扩展</Label>
                  <Switch
                    id="query-expansion"
                    checked={config.enable_query_expansion}
                    onCheckedChange={(checked) => 
                      updateConfig({ enable_query_expansion: checked })
                    }
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>扩展策略</Label>
                  <Select
                    value={config.expansion_strategy}
                    onValueChange={(value) => 
                      updateConfig({ expansion_strategy: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hybrid">混合策略</SelectItem>
                      <SelectItem value="synonyms">同义词扩展</SelectItem>
                      <SelectItem value="paraphrase">句式变换</SelectItem>
                      <SelectItem value="concept">概念扩展</SelectItem>
                      <SelectItem value="question">问题形式</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>扩展数量</Label>
                  <Input
                    type="number"
                    value={config.expansion_count}
                    onChange={(e) => 
                      updateConfig({ expansion_count: parseInt(e.target.value) })
                    }
                    min={1}
                    max={10}
                  />
                </div>
              </CardContent>
            </Card>

            {/* 混合检索配置 */}
            <Card>
              <CardHeader>
                <CardTitle>混合检索</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="hybrid-retrieval">启用混合检索</Label>
                  <Switch
                    id="hybrid-retrieval"
                    checked={config.enable_hybrid_retrieval}
                    onCheckedChange={(checked) => 
                      updateConfig({ enable_hybrid_retrieval: checked })
                    }
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>融合策略</Label>
                  <Select
                    value={config.fusion_strategy}
                    onValueChange={(value) => 
                      updateConfig({ fusion_strategy: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="weighted_sum">加权求和</SelectItem>
                      <SelectItem value="reciprocal_rank">倒数排名融合</SelectItem>
                      <SelectItem value="comb_sum">组合求和</SelectItem>
                      <SelectItem value="comb_mnz">组合最大归一化</SelectItem>
                      <SelectItem value="borda_count">Borda计数</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* 重排序配置 */}
            <Card>
              <CardHeader>
                <CardTitle>重排序</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="reranking">启用重排序</Label>
                  <Switch
                    id="reranking"
                    checked={config.enable_reranking}
                    onCheckedChange={(checked) => 
                      updateConfig({ enable_reranking: checked })
                    }
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>重排序策略</Label>
                  <Select
                    value={config.rerank_strategy}
                    onValueChange={(value) => 
                      updateConfig({ rerank_strategy: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hybrid">混合重排序</SelectItem>
                      <SelectItem value="cross_encoder">Cross-encoder</SelectItem>
                      <SelectItem value="rule_based">规则重排序</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>重排序Top-K</Label>
                  <Input
                    type="number"
                    value={config.rerank_top_k}
                    onChange={(e) => 
                      updateConfig({ rerank_top_k: parseInt(e.target.value) })
                    }
                    min={5}
                    max={100}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="test" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 查询扩展测试 */}
            <Card>
              <CardHeader>
                <CardTitle>查询扩展测试</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>测试查询</Label>
                  <Textarea
                    value={testQuery}
                    onChange={(e) => setTestQuery(e.target.value)}
                    placeholder="输入测试查询..."
                    rows={3}
                  />
                </div>
                <Button 
                  onClick={testQueryExpansion} 
                  disabled={loading || !testQuery.trim()}
                  className="w-full"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  测试查询扩展
                </Button>
                
                {testResults && testResults.expanded_queries && (
                  <div className="space-y-2">
                    <Label>扩展结果</Label>
                    <div className="space-y-1">
                      {testResults.expanded_queries.map((query: string, index: number) => (
                        <Badge key={index} variant="secondary" className="mr-2">
                          {query}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 元数据过滤测试 */}
            <Card>
              <CardHeader>
                <CardTitle>元数据过滤测试</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>选择过滤器</Label>
                  <div className="flex flex-wrap gap-2">
                    {availableFilters.map((filter) => (
                      <Badge
                        key={filter}
                        variant={selectedFilters.includes(filter) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => toggleFilter(filter)}
                      >
                        {filter}
                      </Badge>
                    ))}
                  </div>
                </div>
                <Button 
                  onClick={testMetadataFiltering} 
                  disabled={loading}
                  className="w-full"
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  测试元数据过滤
                </Button>
                
                {testResults && testResults.filter_stats && (
                  <div className="space-y-2">
                    <Label>过滤统计</Label>
                    <div className="text-sm space-y-1">
                      <div>原始文档数: {testResults.filter_stats.original_count}</div>
                      <div>过滤后文档数: {testResults.filter_stats.filtered_count}</div>
                      <div>过滤比例: {(testResults.filter_stats.filter_ratio * 100).toFixed(1)}%</div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="stats" className="space-y-4">
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold">{stats.total_queries}</div>
                  <div className="text-sm text-muted-foreground">总查询数</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-green-600">{stats.successful_queries}</div>
                  <div className="text-sm text-muted-foreground">成功查询</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-red-600">{stats.failed_queries}</div>
                  <div className="text-sm text-muted-foreground">失败查询</div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="text-2xl font-bold">{(stats.avg_processing_time * 1000).toFixed(0)}ms</div>
                  <div className="text-sm text-muted-foreground">平均处理时间</div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EnhancedRetrievalPanel; 