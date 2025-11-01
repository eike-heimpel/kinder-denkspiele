import type { Collection, ObjectId } from 'mongodb';
import { getDatabase } from '$lib/db/client';
import type { User } from '$lib/types';

export class UserRepository {
    private getCollection(): Collection<User> {
        return getDatabase().collection<User>('users');
    }

    async create(name: string, avatar: string): Promise<User> {
        const user: User = {
            name,
            avatar,
            createdAt: new Date()
        };

        const result = await this.getCollection().insertOne(user);
        return {
            ...user,
            _id: result.insertedId.toString()
        };
    }

    async findById(id: string): Promise<User | null> {
        const { ObjectId } = await import('mongodb');
        const user = await this.getCollection().findOne({ _id: new ObjectId(id) as any });

        if (!user) return null;

        return {
            ...user,
            _id: user._id?.toString()
        };
    }

    async findAll(): Promise<User[]> {
        const users = await this.getCollection().find().toArray();
        return users.map(user => ({
            ...user,
            _id: user._id?.toString()
        }));
    }

    async delete(id: string): Promise<boolean> {
        const { ObjectId } = await import('mongodb');
        const result = await this.getCollection().deleteOne({ _id: new ObjectId(id) as any });
        return result.deletedCount > 0;
    }
}
