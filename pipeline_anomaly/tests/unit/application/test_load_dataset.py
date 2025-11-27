import pytest
from unittest.mock import Mock, call

from pipeline_anomaly.application.use_cases.load_dataset import LoadSyntheticDataset
from pipeline_anomaly.domain.models.batch import RecordBatch


class TestLoadSyntheticDataset:
    def test_execute(self):
        mock_generator = Mock()
        mock_writer = Mock()

        batch1 = Mock(spec=RecordBatch)
        batch1.size = 10
        batch2 = Mock(spec=RecordBatch)
        batch2.size = 20
        
        mock_generator.batches.return_value = [batch1, batch2]
        
        use_case = LoadSyntheticDataset(generator=mock_generator, writer=mock_writer)
        use_case.execute()
        
        mock_writer.ensure_schema.assert_called_once()
        assert mock_writer.ingest_batch.call_count == 2
        mock_writer.ingest_batch.assert_has_calls([
            call(batch1),
            call(batch2)
        ])

class TestLoadSyntheticDatasetEdgeCases:
    def test_execute_with_empty_batches(self):
        mock_generator = Mock()
        mock_writer = Mock()

        mock_generator.batches.return_value = []

        use_case = LoadSyntheticDataset(generator=mock_generator, writer=mock_writer)
        use_case.execute()
        
        mock_writer.ensure_schema.assert_called_once()
        mock_writer.ingest_batch.assert_not_called()
    
    def test_execute_with_error_in_schema(self):
        mock_generator = Mock()
        mock_writer = Mock()
        
        # Имитируем ошибку при создании схемы
        mock_writer.ensure_schema.side_effect = Exception("Schema error")
        
        # Act & Assert
        use_case = LoadSyntheticDataset(generator=mock_generator, writer=mock_writer)
        with pytest.raises(Exception, match="Schema error"):
            use_case.execute()
        
        # Проверяем, что ingest_batch не вызывался после ошибки
        mock_writer.ingest_batch.assert_not_called()