import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Image,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { searchRecipes, SearchRecipe, getCoverUrl } from '@/utils/search';
import { isFavorite, toggleFavorite, getFavoriteIds } from '@/utils/favorites';

const CARD_THEMES = ['#f9745b', '#f7b733', '#6dd5ed', '#9b59b6', '#f39c12'];
const API_IMAGE_BASE_URL = 'http://localhost:8000';

export default function SearchScreen() {
  const { q } = useLocalSearchParams<{ q?: string }>();
  const router = useRouter();
  const [keyword, setKeyword] = useState(q || '');
  const [recipes, setRecipes] = useState<SearchRecipe[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const performSearch = useCallback(async (searchKeyword: string, pageNum: number = 1, append: boolean = false) => {
    if (!searchKeyword.trim()) {
      setRecipes([]);
      setHasSearched(false);
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      const result = await searchRecipes(searchKeyword.trim(), pageNum);
      
      if (append) {
        setRecipes((prev) => [...prev, ...result.results]);
      } else {
        setRecipes(result.results);
      }
      
      setTotalCount(result.count);
      setHasMore(!!result.next);
      setPage(pageNum);
      setHasSearched(true);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : '搜索失败');
      setHasSearched(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (q) {
      setKeyword(q);
      performSearch(q);
    }
    setFavoriteIds(getFavoriteIds());
  }, [q, performSearch]);

  const handleRefresh = useCallback(async () => {
    if (!keyword.trim()) return;
    setIsRefreshing(true);
    await performSearch(keyword, 1, false);
    setIsRefreshing(false);
  }, [keyword, performSearch]);

  const handleLoadMore = useCallback(() => {
    if (!isLoading && hasMore && keyword.trim()) {
      performSearch(keyword, page + 1, true);
    }
  }, [isLoading, hasMore, keyword, page, performSearch]);

  const handleSearch = useCallback((searchKeyword: string) => {
    setKeyword(searchKeyword);
    performSearch(searchKeyword, 1, false);
  }, [performSearch]);

  const handleToggleFavorite = useCallback((recipeId: number) => {
    toggleFavorite(recipeId);
    setFavoriteIds(getFavoriteIds());
  }, []);

  const renderItem = ({ item }: { item: SearchRecipe }) => {
    const headerColor = CARD_THEMES[item.id % CARD_THEMES.length];
    const itemIsFavorite = isFavorite(item.id);
    const difficultyStars = '★'.repeat(item.difficulty || 1);
    const emptyStars = '☆'.repeat(Math.max(0, 5 - (item.difficulty || 1)));

    return (
      <Pressable
        style={styles.card}
        onPress={() => router.push({ pathname: '/recipe/[id]', params: { id: item.id.toString() } })}
      >
        <View style={[styles.cardAccent, { backgroundColor: headerColor }]} />
        <Image style={styles.cover} source={{ uri: getCoverUrl(item.cover_url, API_IMAGE_BASE_URL) }} />
        <View style={styles.cardBody}>
          <Text style={styles.cardTitle} numberOfLines={1}>{item.title}</Text>
          <Text style={styles.cardSubtitle}>
            难度：<Text style={styles.difficultyStars}>{difficultyStars}</Text>
            <Text style={styles.difficultyEmpty}>{emptyStars}</Text>
          </Text>
          {item.duration && (
            <Text style={styles.durationText}>耗时：{item.duration}分钟</Text>
          )}
          <View style={styles.cardFooter}>
            {item.dish_type_display && (
              <View style={styles.tags}>
                <Text style={styles.tag}>{item.dish_type_display}</Text>
              </View>
            )}
            <Pressable
              style={styles.favoriteButton}
              onPress={(e) => {
                e.stopPropagation();
                handleToggleFavorite(item.id);
              }}
            >
              <Text style={[styles.heart, itemIsFavorite && styles.heartActive]}>
                {itemIsFavorite ? '♥' : '♡'}
              </Text>
            </Pressable>
          </View>
        </View>
      </Pressable>
    );
  };

  const renderHeader = () => (
    <View style={styles.header}>
      <Pressable style={styles.backButton} onPress={() => router.back()}>
        <Text style={styles.backIcon}>←</Text>
      </Pressable>
      <View style={styles.searchContainer}>
        <View style={styles.inputContainer}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.input}
            placeholder="搜索食谱..."
            placeholderTextColor="#999"
            value={keyword}
            onChangeText={setKeyword}
            onSubmitEditing={() => handleSearch(keyword)}
            returnKeyType="search"
            autoFocus
          />
          {keyword.length > 0 && (
            <Pressable onPress={() => setKeyword('')} style={styles.clearButton}>
              <Text style={styles.clearIcon}>✕</Text>
            </Pressable>
          )}
        </View>
        <Pressable
          style={[styles.searchButton, !keyword.trim() && styles.searchButtonDisabled]}
          onPress={() => handleSearch(keyword)}
          disabled={!keyword.trim()}
        >
          <Text style={styles.searchButtonText}>搜索</Text>
        </Pressable>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {renderHeader()}
      
      {isLoading && !hasSearched && (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#c28f00" />
        </View>
      )}

      {error && (
        <View style={styles.centerContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <Pressable style={styles.retryButton} onPress={() => handleSearch(keyword)}>
            <Text style={styles.retryText}>重试</Text>
          </Pressable>
        </View>
      )}

      {!error && hasSearched && (
        <View style={styles.resultHeader}>
          <Text style={styles.resultCount}>
            {totalCount > 0 ? `找到 ${totalCount} 道食谱` : '未找到相关食谱'}
          </Text>
        </View>
      )}

      {!error && (
        <FlatList
          data={recipes}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} tintColor="#c28f00" />
          }
          onEndReached={handleLoadMore}
          onEndReachedThreshold={0.5}
          ListFooterComponent={
            hasMore && isLoading ? (
              <View style={styles.footerLoader}>
                <ActivityIndicator size="small" color="#c28f00" />
              </View>
            ) : null
          }
          ListEmptyComponent={
            hasSearched && !isLoading ? (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyIcon}>🔍</Text>
                <Text style={styles.emptyText}>未找到相关食谱</Text>
                <Text style={styles.emptyHint}>试试其他关键词吧</Text>
              </View>
            ) : null
          }
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f6f2ec',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    gap: 8,
  },
  backButton: {
    padding: 4,
  },
  backIcon: {
    fontSize: 24,
    color: '#333',
  },
  searchContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
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
  resultHeader: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#f6f2ec',
  },
  resultCount: {
    fontSize: 14,
    color: '#666',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  card: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 16,
    marginVertical: 6,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 3,
  },
  cardAccent: {
    width: 6,
  },
  cover: {
    width: 100,
    height: 100,
  },
  cardBody: {
    flex: 1,
    padding: 12,
    justifyContent: 'space-between',
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: '#333',
  },
  cardSubtitle: {
    fontSize: 13,
    color: '#666',
    marginTop: 4,
  },
  durationText: {
    fontSize: 12,
    color: '#999',
    marginTop: 2,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  tags: {
    flexDirection: 'row',
    gap: 6,
  },
  tag: {
    backgroundColor: '#f0ede8',
    color: '#6c6c6c',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    fontSize: 11,
  },
  favoriteButton: {
    padding: 4,
  },
  heart: {
    fontSize: 20,
    color: '#b6b6b6',
  },
  heartActive: {
    color: '#e74c3c',
  },
  difficultyStars: {
    color: '#f5c542',
  },
  difficultyEmpty: {
    color: '#ddd',
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  errorText: {
    color: '#c0392b',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 16,
  },
  retryButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    backgroundColor: '#f9745b',
    borderRadius: 20,
  },
  retryText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyIcon: {
    fontSize: 64,
    color: '#ddd',
    marginBottom: 16,
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
    marginBottom: 8,
  },
  emptyHint: {
    fontSize: 13,
    color: '#bbb',
  },
  footerLoader: {
    paddingVertical: 20,
    alignItems: 'center',
  },
});
