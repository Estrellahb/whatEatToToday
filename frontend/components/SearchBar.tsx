import React, { useState } from 'react';
import {
  StyleSheet,
  TextInput,
  View,
  Pressable,
  Text,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (keyword: string) => void;
  autoFocus?: boolean;
}

export default function SearchBar({
  placeholder = '搜索食谱...',
  onSearch,
  autoFocus = false,
}: SearchBarProps) {
  const router = useRouter();
  const [keyword, setKeyword] = useState('');

  const handleSearch = () => {
    const trimmedKeyword = keyword.trim();
    if (trimmedKeyword) {
      if (onSearch) {
        onSearch(trimmedKeyword);
      } else {
        router.push({
          pathname: '/search',
          params: { q: trimmedKeyword },
        });
      }
    }
  };

  const handleClear = () => {
    setKeyword('');
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputContainer}>
        <Text style={styles.searchIcon}>🔍</Text>
        <TextInput
          style={styles.input}
          placeholder={placeholder}
          placeholderTextColor="#999"
          value={keyword}
          onChangeText={setKeyword}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
          autoFocus={autoFocus}
          clearButtonMode="while-editing"
        />
        {keyword.length > 0 && (
          <Pressable onPress={handleClear} style={styles.clearButton}>
            <Text style={styles.clearIcon}>✕</Text>
          </Pressable>
        )}
      </View>
      <Pressable
        style={[styles.searchButton, !keyword.trim() && styles.searchButtonDisabled]}
        onPress={handleSearch}
        disabled={!keyword.trim()}
      >
        <Text style={styles.searchButtonText}>搜索</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
  },
  inputContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 20,
    paddingHorizontal: 12,
    height: 40,
  },
  searchIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  input: {
    flex: 1,
    fontSize: 15,
    color: '#333',
    paddingVertical: 0,
    outlineWidth: 0,
    outline: 'none',
  },
  clearButton: {
    padding: 4,
    marginLeft: 4,
  },
  clearIcon: {
    fontSize: 16,
    color: '#999',
  },
  searchButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#f9745b',
    borderRadius: 20,
    minWidth: 60,
    alignItems: 'center',
    justifyContent: 'center',
  },
  searchButtonDisabled: {
    backgroundColor: '#ddd',
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
});
