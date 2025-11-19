class ModelConfig:
    def __init__(self, excel_path, skiprows, category_threshold, model_name, max_seq_length, learning_rate, batch_size, num_epochs, output_dir):
        self.excel_path = excel_path
        self.skiprows = skiprows
        self.category_threshold = category_threshold
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.learning_rate = learning_rate
        self.batch = batch_size
        self.num_epochs = num_epochs
        self.output_dir = output_dir