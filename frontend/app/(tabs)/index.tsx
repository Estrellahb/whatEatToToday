import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  SectionList,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { isFavorite, toggleFavorite, getFavoriteIds } from '@/utils/favorites';
import SearchBar from '@/components/SearchBar';
import RecipeImage from '@/components/RecipeImage';
import { getRecommendations, Recipe } from '@/utils/localData';

const CARD_THEMES = ['#f9745b', '#f7b733', '#6dd5ed', '#9b59b6', '#f39c12'];

const MEAL_SECTIONS = [
  { key: 'breakfast', title: '🌅 早餐', mealType: 'breakfast', count: 2 },
  { key: 'lunch', title: '☀️ 午餐', mealType: 'lunch', count: 3 },
  { key: 'dinner', title: '🌙 晚餐', mealType: 'dinner', count: 3 },
  { key: 'dessert', title: '🍰 甜点', mealType: 'dessert', count: 1 },
  { key: 'drink', title: '🥤 饮品', mealType: 'drink', count: 1 },
];

interface Section {
  key: string;
  title: string;
  data: Recipe[];
}

export default function HomeScreen() {
  const router = useRouter();
  const [sections, setSections] = useState<Section[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [favoriteIds, setFavoriteIds] = useState<number[]>([]);

  const fetchRecipes = useCallback(async () => {
    try {
      setError('');
      // 并行获取各餐段的随机推荐
      const results = MEAL_SECTIONS.map(({ key, title, mealType, count }) => {
        const data = getRecommendations(mealType, count);
        return { key, title, data };
      });
      setSections(results.filter((s) => s.data.length > 0));
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : '加载失败');
    }
  }, []);

  useEffect(() => {
    setIsLoading(true);
    fetchRecipes().finally(() => setIsLoading(false));
    // 加载收藏状态
    setFavoriteIds(getFavoriteIds());
  }, [fetchRecipes]);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await fetchRecipes();
    setIsRefreshing(false);
  }, [fetchRecipes]);

  // 单个餐段换一批
  const [refreshingKeys, setRefreshingKeys] = useState<Record<string, boolean>>({});

  const refreshSection = useCallback(async (sectionKey: string) => {
    const config = MEAL_SECTIONS.find((s) => s.key === sectionKey);
    if (!config) return;

    setRefreshingKeys((prev) => ({ ...prev, [sectionKey]: true }));
    try {
      const data = getRecommendations(config.mealType, config.count);
      setSections((prev) =>
        prev.map((s) => (s.key === sectionKey ? { ...s, data } : s))
      );
    } finally {
      setRefreshingKeys((prev) => ({ ...prev, [sectionKey]: false }));
    }
  }, []);

  const renderSectionHeader = ({ section }: { section: Section }) => (
    <View style={styles.sectionHeader}>
      <View style={styles.sectionLeft}>
        <Text style={styles.sectionTitle}>{section.title}</Text>
        <Text style={styles.sectionCount}>{section.data.length} 道</Text>
      </View>
      <Pressable
        style={styles.refreshSectionButton}
        onPress={() => refreshSection(section.key)}
        disabled={refreshingKeys[section.key]}
      >
        <Text style={[styles.refreshSectionText, refreshingKeys[section.key] && styles.refreshingText]}>
          {refreshingKeys[section.key] ? '加载中...' : '换一批'}
        </Text>
      </Pressable>
    </View>
  );

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
        <RecipeImage
          title={item.title}
          dishType={item.dish_type}
          style={styles.cover}
          resizeMode="cover"
        />
        <View style={styles.cardBody}>
          <Text style={styles.cardTitle} numberOfLines={1}>{item.title}</Text>
          <Text style={styles.cardSubtitle}>
            难度：<Text style={styles.difficultyStars}>{difficultyStars}</Text>
            <Text style={styles.difficultyEmpty}>{emptyStars}</Text>
          </Text>
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
                toggleFavorite(item.id);
                setFavoriteIds(getFavoriteIds());
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
        <Pressable style={styles.retryButton} onPress={() => fetchRecipes()}>
          <Text style={styles.retryText}>重试</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <SearchBar />
      <SectionList
        sections={sections}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        renderSectionHeader={renderSectionHeader}
        stickySectionHeadersEnabled
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} tintColor="#c28f00" />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>暂无食谱</Text>
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
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#f6f2ec',
    paddingVertical: 12,
    paddingHorizontal: 4,
    marginTop: 8,
  },
  sectionLeft: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 8,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  sectionCount: {
    fontSize: 13,
    color: '#999',
  },
  refreshSectionButton: {
    paddingVertical: 4,
    paddingHorizontal: 10,
  },
  refreshSectionText: {
    fontSize: 13,
    color: '#f9745b',
  },
  refreshingText: {
    color: '#999',
  },
  card: {
    flexDirection: 'row',
    alignItems: 'stretch',
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
    // 样式已移至 RecipeImage 组件内部
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
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 15,
    color: '#999',
  },
});
