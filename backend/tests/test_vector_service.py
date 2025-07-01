"""
向量化服务测试
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from app.services.vector_service import VectorService
from app.models.knowledge_base import KnowledgeBaseChunk as TextChunk, KnowledgeBaseImage as ImageVector
from app.core.config import settings


class TestVectorService:
    """向量化服务测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def vector_service(self, mock_db):
        """创建向量化服务实例"""
        with patch('app.services.vector_service.qdrant_client.QdrantClient'):
            return VectorService(mock_db)
    
    def test_simple_text_embedding(self, vector_service):
        """测试简单文本向量化"""
        text = "Hello world"
        embedding = vector_service._simple_text_embedding(text)
        
        assert len(embedding) == settings.TEXT_EMBEDDING_DIMENSION
        assert all(isinstance(x, float) for x in embedding)
        assert abs(sum(x * x for x in embedding) - 1.0) < 1e-6  # 归一化检查
    
    @pytest.mark.asyncio
    async def test_get_text_embedding_with_openai(self, vector_service):
        """测试OpenAI文本向量化"""
        with patch('app.services.vector_service.settings.OPENAI_API_KEY', 'test_key'):
            with patch('aiohttp.ClientSession') as mock_session:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={
                    "data": [{"embedding": [0.1] * settings.TEXT_EMBEDDING_DIMENSION}]
                })
                
                mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
                
                embedding = await vector_service.get_text_embedding("test text")
                
                assert len(embedding) == settings.TEXT_EMBEDDING_DIMENSION
                assert all(x == 0.1 for x in embedding)
    
    @pytest.mark.asyncio
    async def test_get_text_embedding_fallback(self, vector_service):
        """测试文本向量化降级"""
        with patch('app.services.vector_service.settings.OPENAI_API_KEY', None):
            embedding = await vector_service.get_text_embedding("test text")
            
            assert len(embedding) == settings.TEXT_EMBEDDING_DIMENSION
            assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_get_image_embedding(self, vector_service):
        """测试图片向量化"""
        image_path = "test_image.jpg"
        embedding = await vector_service.get_image_embedding(image_path)
        
        assert len(embedding) == settings.IMAGE_EMBEDDING_DIMENSION
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_vectorize_text_chunk(self, vector_service):
        """测试文本分块向量化"""
        # 创建模拟文本分块
        chunk = Mock(spec=TextChunk)
        chunk.id = "test-chunk-id"
        chunk.content = "test content"
        chunk.source_file = "test.txt"
        chunk.chunk_index = 0
        chunk.knowledge_base_id = "test-kb-id"
        chunk.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        
        with patch.object(vector_service, 'get_text_embedding', return_value=[0.1] * settings.TEXT_EMBEDDING_DIMENSION):
            with patch.object(vector_service.qdrant_client, 'upsert') as mock_upsert:
                result = await vector_service.vectorize_text_chunk(chunk)
                
                assert result is True
                mock_upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_vectorize_image(self, vector_service):
        """测试图片向量化"""
        # 创建模拟图片
        image = Mock(spec=ImageVector)
        image.id = "test-image-id"
        image.filename = "test.jpg"
        image.description = "test image"
        image.knowledge_base_id = "test-kb-id"
        image.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        
        with patch.object(vector_service, 'get_image_embedding', return_value=[0.1] * settings.IMAGE_EMBEDDING_DIMENSION):
            with patch.object(vector_service.qdrant_client, 'upsert') as mock_upsert:
                result = await vector_service.vectorize_image(image)
                
                assert result is True
                mock_upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_text(self, vector_service):
        """测试文本搜索"""
        query = "test query"
        kb_ids = ["kb1", "kb2"]
        
        with patch.object(vector_service, 'get_text_embedding', return_value=[0.1] * settings.TEXT_EMBEDDING_DIMENSION):
            with patch.object(vector_service.qdrant_client, 'search') as mock_search:
                mock_result = Mock()
                mock_result.id = "result1"
                mock_result.score = 0.95
                mock_result.payload = {
                    "content": "test content",
                    "source_file": "test.txt",
                    "chunk_index": 0,
                    "knowledge_base_id": "kb1"
                }
                mock_search.return_value = [mock_result]
                
                results = await vector_service.search_text(query, kb_ids)
                
                assert len(results) == 1
                assert results[0]["id"] == "result1"
                assert results[0]["score"] == 0.95
                assert results[0]["content"] == "test content"
    
    @pytest.mark.asyncio
    async def test_search_image(self, vector_service):
        """测试图片搜索"""
        query = "test query"
        kb_ids = ["kb1", "kb2"]
        
        with patch.object(vector_service, 'get_text_embedding', return_value=[0.1] * settings.TEXT_EMBEDDING_DIMENSION):
            with patch.object(vector_service.qdrant_client, 'search') as mock_search:
                mock_result = Mock()
                mock_result.id = "result1"
                mock_result.score = 0.85
                mock_result.payload = {
                    "filename": "test.jpg",
                    "description": "test image",
                    "knowledge_base_id": "kb1"
                }
                mock_search.return_value = [mock_result]
                
                results = await vector_service.search_image(query, kb_ids)
                
                assert len(results) == 1
                assert results[0]["id"] == "result1"
                assert results[0]["score"] == 0.85
                assert results[0]["filename"] == "test.jpg"
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, vector_service):
        """测试混合搜索"""
        query = "test query"
        kb_ids = ["kb1"]
        
        with patch.object(vector_service, 'search_text', return_value=[{"id": "text1", "score": 0.9}]):
            with patch.object(vector_service, 'search_image', return_value=[{"id": "image1", "score": 0.8}]):
                results = await vector_service.hybrid_search(query, kb_ids)
                
                assert "text" in results
                assert "image" in results
                assert len(results["text"]) == 1
                assert len(results["image"]) == 1
                assert results["text"][0]["id"] == "text1"
                assert results["image"][0]["id"] == "image1" 