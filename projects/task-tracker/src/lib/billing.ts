import { prisma } from './prisma';

export type CreditTransaction = {
  id: string;
  userId: string;
  amount: number;
  source: string;
  stripeId: string | null;
  description: string | null;
  createdAt: Date;
};

export async function getCreditBalance(userId: string): Promise<number> {
  const result = await prisma.creditTransaction.aggregate({
    where: { userId },
    _sum: { amount: true },
  });
  return result._sum.amount ?? 0;
}

export async function addCredits(
  userId: string,
  amount: number,
  source: string = 'stripe',
  stripeId: string = '',
  description: string = ''
): Promise<CreditTransaction> {
  if (amount <= 0) {
    throw new Error('Credit amount must be positive');
  }

  const tx = await prisma.creditTransaction.create({
    data: {
      userId,
      amount,
      source,
      stripeId: stripeId || null,
      description: description || null,
    },
  });

  return tx;
}

export async function spendCredits(
  userId: string,
  amount: number,
  description: string = ''
): Promise<CreditTransaction> {
  if (amount <= 0) {
    throw new Error('Spend amount must be positive');
  }

  const balance = await getCreditBalance(userId);
  if (balance < amount) {
    throw new Error(`Insufficient credits: have ${balance}, need ${amount}`);
  }

  const tx = await prisma.creditTransaction.create({
    data: {
      userId,
      amount: -amount,
      source: 'spend',
      description: description || null,
    },
  });

  return tx;
}

export async function getTransactionHistory(
  userId: string,
  limit: number = 50
): Promise<CreditTransaction[]> {
  return prisma.creditTransaction.findMany({
    where: { userId },
    orderBy: { createdAt: 'desc' },
    take: limit,
  });
}
