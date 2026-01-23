import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Image,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useFocusEffect } from 'expo-router';
import { getFavoriteIds, toggleFavorite, isFavorite } from '@/utils/favorites';

const API_BASE_URL = 'http://localhost:8000/api/v1';
const API_IMAGE_BASE_URL = 'http://localhost:8000';
const CARD_THEMES = ['#f9745b', '#f7b733', '#6dd5ed', '#9b59b6', '#f39c12'];

interface Recipe {
  id: number;
  title: string;
  difficulty: number;
  difficulty_display?: string;
  cover_url?: string | null;
  meal_types_display?: string[];
  dish_type_display?: string;
  duration?: number;
}

const getCoverUrl = (coverUrl?: string | null) => {
  if (!coverUrl) {
    return 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80';
  }
  if (coverUrl.startsWith('http')) {
    return coverUrl;
  }
  return `${API_IMAGE_BASE_URL}/${coverUrl}`;
};

export default function FavoritesScreen() {
  const router = useRouter();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);

  const fetchFavoriteRecipes = useCallback(async () => {
    try {
      setError('');
      const ids = getFavoriteIds();
      setFavoriteIds(ids);

      if (ids.length === 0) {
        setRecipes([]);
        return;
      }

      // 并行获取所有收藏的食谱详情
      const results = await Promise.all(
        ids.map(async (id) => {
          try {
            const response = await fetch(`${API_BASE_URL}/recipes/${id}/`);
            if (!response.ok) {
              return null;
            }
            const data = (await response.json()) as Recipe;
            return data;
          } catch {
            return null;
          }
        })
      );

      const validRecipes = results.filter((r): r is Recipe => r !== null);
      setRecipes(validRecipes);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : '加载失败');
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      setIsLoading(true);
      fetchFavoriteRecipes().finally(() => setIsLoading(false));
    }, [fetchFavoriteRecipes])
  );

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await fetchFavoriteRecipes();
    setIsRefreshing(false);
  }, [fetchFavoriteRecipes]);

  const handleToggleFavorite = useCallback((recipeId: number) => {
    toggleFavorite(recipeId);
    const newIds = getFavoriteIds();
    setFavoriteIds(newIds);
    // 如果取消收藏，从列表中移除
    if (!newIds.includes(recipeId)) {
      setRecipes((prev) => prev.filter((r) => r.id !== recipeId));
    }
  }, []);

  const renderItem = ({ item }: { item: Recipe }) => {
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
        <Image style={styles.cover} source={{ uri: getCoverUrl(item.cover_url) }} />
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

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#c28f00" />
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>{error}</Text>
        <Pressable style={styles.retryButton} onPress={() => fetchFavoriteRecipes()}>
          <Text style={styles.retryText}>重试</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>我的收藏</Text>
        <View style={styles.headerCountContainer}>
          <Text style={styles.headerCount}>{recipes.length} 道</Text>
        </View>
      </View>
      <FlatList
        data={recipes}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} tintColor="#c28f00" />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyIcon}>♡</Text>
            <Text style={styles.emptyText}>还没有收藏的食谱</Text>
            <Text style={styles.emptyHint}>去首页发现更多美食吧</Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f6f2ec',
  },
  header: {
    flexDirection: 'column',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#333',
  },
  headerCountContainer: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 4,
  },
  headerCount: {
    fontSize: 14,
    color: '#999',
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
  errorText: {
    color: '#c0392b',
    fontSize: 14,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 16,
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
});
