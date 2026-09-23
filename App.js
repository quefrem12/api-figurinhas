import * as FileSystem from 'expo-file-system';
import { useState } from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import RNWhatsAppStickers from 'react-native-whatsapp-stickers';
import { unzip } from 'react-native-zip-archive';

export default function App() {
  const [loading, setLoading] = useState(false);

  // Seu IP e porta do Flask
  const URL_DOWNLOAD = "https://api-figurinhas-production.up.railway.app/baixar_zip";

  const baixarEImportar = async () => {
    setLoading(true);
    try {
      // 1. Caminhos dos arquivos
      const zipUri = `${FileSystem.documentDirectory}novas_figurinhas.zip`;
      const pastaDestino = `${FileSystem.documentDirectory}figurinhas_descompactadas`;

      // 2. Baixa o ZIP
      const downloadRes = await FileSystem.downloadAsync(URL_DOWNLOAD, zipUri);
      if (downloadRes.status !== 200) {
        throw new Error("Não foi possível baixar o arquivo do PC.");
      }

      // 3. Cria a pasta de destino (se não existir) e descompacta
      const pastaInfo = await FileSystem.getInfoAsync(pastaDestino);
      if (!pastaInfo.exists) {
        await FileSystem.makeDirectoryAsync(pastaDestino);
      }
      
      await unzip(zipUri, pastaDestino);

      // 4. Envia para o WhatsApp (O pacote e a estrutura precisam estar perfeitos)
      await RNWhatsAppStickers.send('meu_pacote_id', 'Figurinhas do PC');
      Alert.alert('Sucesso!', 'Figurinhas enviadas para o WhatsApp!');

    } catch (error) {
      Alert.alert('Erro no Processo', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>📥 Importador Zap</Text>
      <Text style={styles.subtitle}>Puxe as figurinhas do PC com 1 clique</Text>

      <TouchableOpacity style={styles.button} onPress={baixarEImportar} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Puxar do PC e Enviar</Text>
        )}
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#ece5dd' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#075e54', marginBottom: 10 },
  subtitle: { fontSize: 16, color: '#333', marginBottom: 40 },
  button: { backgroundColor: '#25d366', padding: 20, borderRadius: 50, elevation: 5 },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' }
});