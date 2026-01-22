import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  View,
  Pressable,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';

const API_BASE_URL = 'http://localhost:8000/api/v1';
const API_IMAGE_BASE_URL = 'http://localhost:8000';

interface Ingredient {
  ingredient_id: number;
  ingredient_name: string;
  ingredient_category: string;
  amount: string;
}

interface Step {
  step: number;
  description: string;
}

interface RecipeDetail {
  id: number;
  title: string;
  difficulty: number;
  difficulty_display?: string;
  duration: number;
  cover_url?: string | null;
  meal_types_display?: string[];
  servings?: number | null;
  steps: Step[];
  tools: string[];
  tips?: string;
  ingredients: Ingredient[];
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

export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRecipeDetail = async () => {
      try {
        setIsLoading(true);
        setError('');
        const response = await fetch(`${API_BASE_URL}/recipes/${id}/`);
        if (!response.ok) {
          throw new Error('请求失败');
        }
        const data = (await response.json()) as RecipeDetail;
        setRecipe(data);
      } catch (fetchError) {
        setError(fetchError instanceof Error ? fetchError.message : '加载失败');
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchRecipeDetail();
    }
  }, [id]);

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#c28f00" />
      </SafeAreaView>
    );
  }

  if (error || !recipe) {
    return (
      <SafeAreaView style={styles.container}>
        <Text style={styles.errorText}>{error || '菜谱不存在'}</Text>
        <Pressable style={styles.backButton} onPress={() => router.back()}>
          <Text style={styles.backButtonText}>返回</Text>
        </Pressable>
      </SafeAreaView>
    );
  }

  const difficultyStars = '★'.repeat(recipe.difficulty || 1);
  const emptyStars = '☆'.repeat(Math.max(0, 5 - (recipe.difficulty || 1)));
  const mealLabel = recipe.meal_types_display?.join(' / ') ?? '';

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* 返回按钮 */}
        <Pressable style={styles.backHeader} onPress={() => router.back()}>
          <Text style={styles.backIcon}>←</Text>
          <Text style={styles.backText}>返回</Text>
        </Pressable>

        {/* 封面图 */}
        <Image style={styles.coverImage} source={{ uri: getCoverUrl(recipe.cover_url) }} />

        {/* 标题区 */}
        <View style={styles.headerSection}>
          <Text style={styles.title}>{recipe.title}</Text>
          <View style={styles.metaRow}>
            <Text style={styles.metaText}>
              难度：<Text style={styles.stars}>{difficultyStars}</Text>
              <Text style={styles.starsEmpty}>{emptyStars}</Text>
            </Text>
            <Text style={styles.metaText}>耗时：{recipe.duration}分钟</Text>
          </View>
          {mealLabel && <Text style={styles.mealLabel}>{mealLabel}</Text>}
        </View>

        {/* 食材 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>食材准备</Text>
          <View style={styles.ingredientsList}>
            {recipe.ingredients.map((item) => (
              <View key={item.ingredient_id} style={styles.ingredientItem}>
                <Text style={styles.ingredientName}>{item.ingredient_name}</Text>
                <Text style={styles.ingredientAmount}>{item.amount}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* 步骤 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>制作步骤</Text>
          {recipe.steps.map((step) => (
            <View key={step.step} style={styles.stepItem}>
              <View style={styles.stepNumber}>
                <Text style={styles.stepNumberText}>{step.step}</Text>
              </View>
              <Text style={styles.stepDescription}>{step.description}</Text>
            </View>
          ))}
        </View>

        {/* 小贴士 */}
        {recipe.tips && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>小贴士</Text>
            <View style={styles.tipsBox}>
              <Text style={styles.tipsText}>{recipe.tips}</Text>
            </View>
          </View>
        )}

        {/* 底部留白 */}
        <View style={styles.bottomSpacer} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f6f2ec',
  },
  scrollView: {
    flex: 1,
  },
  backHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backIcon: {
    fontSize: 20,
    color: '#333',
    marginRight: 6,
  },
  backText: {
    fontSize: 16,
    color: '#333',
  },
  coverImage: {
    width: '100%',
    height: 240,
  },
  headerSection: {
    backgroundColor: '#fff',
    paddingHorizontal: 20,
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
    fontSize: 28,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  metaRow: {
    flexDirection: 'row',
    gap: 20,
    marginBottom: 8,
  },
  metaText: {
    fontSize: 14,
    color: '#666',
  },
  stars: {
    color: '#f5c542',
  },
  starsEmpty: {
    color: '#ddd',
  },
  mealLabel: {
    fontSize: 13,
    color: '#999',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 12,
    paddingHorizontal: 20,
    paddingVertical: 18,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  ingredientsList: {
    gap: 10,
  },
  ingredientItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  ingredientName: {
    fontSize: 15,
    color: '#333',
  },
  ingredientAmount: {
    fontSize: 15,
    color: '#999',
  },
  stepItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  stepNumber: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#f9745b',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
    flexShrink: 0,
  },
  stepNumberText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  stepDescription: {
    flex: 1,
    fontSize: 15,
    color: '#444',
    lineHeight: 24,
  },
  tipsBox: {
    backgroundColor: '#fffbf0',
    borderLeftWidth: 3,
    borderLeftColor: '#f5c542',
    paddingHorizontal: 14,
    paddingVertical: 12,
    borderRadius: 4,
  },
  tipsText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  bottomSpacer: {
    height: 40,
  },
  errorText: {
    color: '#c0392b',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  backButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    backgroundColor: '#f9745b',
    borderRadius: 20,
  },
  backButtonText: {
    color: '#fff',
    fontSize: 14,
  },
});
