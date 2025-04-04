using System.Text;


namespace FileReader {
    public class FileReader {
        private static IEnumerable<string?> ReadFile(string path) {
            if (!File.Exists(path)) {
                throw new FileNotFoundException();
            }

            using var reader = new StreamReader(path, Encoding.GetEncoding("latin1"));
            while (!reader.EndOfStream) {
                yield return reader.ReadLine();
            }
        }

        public static void Main(string[] args) {
            if (args.Length != 1) {
                Console.WriteLine("Usage: FileReader <file path>");
                Environment.Exit(1);
            }

            string filePath = args[0];

            try {
                foreach(var line in ReadFile(filePath)) {
                    Console.WriteLine(line);
                }
                Environment.Exit(0);
            }
            catch (FileNotFoundException) {
                Console.Error.WriteLine($"Error file not found at {filePath}");
                Environment.Exit(2);
            }
            catch (Exception ex) {
                Console.Error.WriteLine($"Unexpected error {ex}");
                    Environment.Exit(3);
            }
        }
    }
}