import type { Collection } from 'mongodb';
import { getDatabase } from '$lib/db/client';
import type { GameSession, GameSessionDocument, GameType, DifficultyLevel, GameStats } from '$lib/types';

export class GameSessionRepository {
    private getCollection(): Collection<GameSessionDocument> {
        return getDatabase().collection<GameSessionDocument>('game_sessions');
    }

    async create(session: Omit<GameSession, '_id'>): Promise<GameSession> {
        const doc: Omit<GameSessionDocument, '_id'> = {
            ...session,
            seenWords: session.seenWords ? Array.from(session.seenWords) : undefined
        };

        const result = await this.getCollection().insertOne(doc);
        return {
            ...session,
            _id: result.insertedId.toString()
        };
    }

    async update(id: string, updates: Partial<GameSession>): Promise<void> {
        const { ObjectId } = await import('mongodb');
        const updateDoc: any = { ...updates };

        // Remove _id from updates to avoid MongoDB errors
        delete updateDoc._id;

        // Convert Set to Array for MongoDB
        if (updates.seenWords) {
            updateDoc.seenWords = Array.from(updates.seenWords);
        }

        await this.getCollection().updateOne(
            { _id: new ObjectId(id) as any },
            { $set: updateDoc }
        );
    }

    async findById(id: string): Promise<GameSession | null> {
        const { ObjectId } = await import('mongodb');
        const doc = await this.getCollection().findOne({ _id: new ObjectId(id) as any });

        if (!doc) return null;

        return {
            ...doc,
            _id: doc._id?.toString(),
            seenWords: doc.seenWords ? new Set(doc.seenWords) : undefined
        };
    }

    async findActiveByUserId(userId: string, gameType: GameType): Promise<GameSession | null> {
        const doc = await this.getCollection().findOne({
            userId,
            gameType,
            isActive: true
        });

        if (!doc) return null;

        return {
            ...doc,
            _id: doc._id?.toString(),
            seenWords: doc.seenWords ? new Set(doc.seenWords) : undefined
        };
    }

    async getStatsByUser(userId: string, gameType: GameType, difficulty: DifficultyLevel): Promise<GameStats> {
        const sessions = await this.getCollection()
            .find({
                userId,
                gameType,
                difficulty,
                isActive: false
            })
            .toArray();

        if (sessions.length === 0) {
            return {
                totalGames: 0,
                highScore: 0,
                averageScore: 0
            };
        }

        const scores = sessions.map(s => s.score);
        const highScore = Math.max(...scores);
        const averageScore = scores.reduce((a, b) => a + b, 0) / scores.length;
        const lastPlayed = sessions
            .filter(s => s.endedAt)
            .sort((a, b) => b.endedAt!.getTime() - a.endedAt!.getTime())[0]?.endedAt;

        return {
            totalGames: sessions.length,
            highScore,
            averageScore: Math.round(averageScore),
            lastPlayed
        };
    }
}
