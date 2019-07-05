# Generated by Django 2.2.1 on 2019-07-04 15:47

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.CharField(max_length=64, unique=True)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('sequence_next', models.IntegerField(default=1)),
                ('registered', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=20, null=True)),
                ('photo', models.ImageField(null=True, upload_to='account_photos/')),
                ('photo_hash', models.CharField(max_length=128, null=True)),
                ('registered_date', models.DateTimeField(null=True)),
                ('linked', models.BooleanField(default=False)),
                ('degree', models.IntegerField(default=0)),
                ('key', models.DecimalField(decimal_places=998, max_digits=999, null=True)),
                ('committed', models.BooleanField()),
                ('committed_time', models.DateTimeField(null=True)),
                ('committed_hash', models.CharField(max_length=128, null=True)),
                ('balance_due', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('balance_due_last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('settlement_countdown', models.DateTimeField(null=True)),
                ('last_position', models.IntegerField(default=0)),
                ('net_votes', models.IntegerField(default=0)),
                ('matched_count', models.IntegerField(default=0)),
                ('chalenges_degree', models.IntegerField(default=0)),
                ('chalenges_key', models.DecimalField(decimal_places=199, max_digits=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Arrow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Neutral'), (1, 'Trust'), (-1, 'Distrust')], default=0)),
                ('matched', models.BooleanField(default=False)),
                ('position', models.IntegerField(null=True)),
                ('expired', models.BooleanField(default=False)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_arrows', to='core.Account')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_arrows', to='core.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(null=True)),
                ('linked', models.BooleanField(default=False)),
                ('degree', models.IntegerField(default=0)),
                ('finished', models.BooleanField(default=False)),
                ('settlement_countdown', models.DateTimeField(null=True)),
                ('last_position', models.IntegerField(default=0)),
                ('net_votes', models.IntegerField(default=0)),
                ('matched_count', models.IntegerField(default=0)),
                ('last_position_who', models.IntegerField(default=0)),
                ('net_votes_who', models.IntegerField(default=0)),
                ('matched_count_who', models.IntegerField(default=0)),
                ('challenger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challenges_created', to='core.Account')),
                ('defendant_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challenges_against_1', to='core.Account')),
                ('defendant_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challenges_against_2', to='core.Account')),
            ],
        ),
        migrations.CreateModel(
            name='ChallengeLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'neutral'), (1, 'support'), (-1, 'oppose')], default=0)),
                ('matched', models.BooleanField(default=False)),
                ('position', models.IntegerField(null=True)),
                ('status_who', models.IntegerField(choices=[(0, 'neutral'), (1, 'd1good'), (-1, 'd2good')], default=0)),
                ('matched_who', models.BooleanField(default=False)),
                ('position_who', models.IntegerField(null=True)),
                ('expired', models.BooleanField(default=False)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challengelinks', to='core.Challenge')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challengelinks', to='core.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Commitment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('committed_hash', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('event_type', models.CharField(choices=[('Txn', 'Transaction'), ('AC', 'ArrowCreation'), ('AE', 'ArrowExpiration'), ('MS', 'MarketSettlement'), ('MST', 'MarketSettlementTransfer'), ('BU', 'BalanceUpdate'), ('CLC', 'ChallengeLinkCreation'), ('CLE', 'ChallengeLinkExpiration'), ('CS', 'ChallengeSettlement'), ('CST', 'ChallengeSettlementTransfer')], max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='EventCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_event_no', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MarketSettlement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Txn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('txn_previous_hash', models.CharField(max_length=128)),
                ('txn_type', models.CharField(choices=[('Transfer', 'Transfer'), ('Commitment', 'Commitment'), ('Revealation', 'Revealation'), ('Registration', 'Registration'), ('ChangeVote', 'ChangeVote'), ('Challenge', 'Challenge'), ('ChangeChallengeVote', 'ChangeChallengeVote')], max_length=20)),
                ('sender_seq_no', models.IntegerField()),
                ('txn_message', models.CharField(max_length=328)),
                ('signature', models.CharField(max_length=128)),
                ('txn_data', models.CharField(max_length=1328)),
                ('txn_hash', models.CharField(max_length=128)),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Event')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_recieved', to='core.Account')),
                ('txn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn')),
            ],
        ),
        migrations.CreateModel(
            name='Revelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('revealed_value', models.CharField(max_length=128)),
                ('commitment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='revelation', to='core.Commitment')),
                ('txn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn')),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=30)),
                ('photo_hash', models.CharField(max_length=128)),
                ('txn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn')),
            ],
        ),
        migrations.CreateModel(
            name='MarketSettlementTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Event')),
                ('market_settlement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.MarketSettlement')),
                ('payee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
            ],
        ),
        migrations.AddField(
            model_name='commitment',
            name='txn',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn'),
        ),
        migrations.CreateModel(
            name='ChallengeLinkCreation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challengelink', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.ChallengeLink')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Event')),
            ],
        ),
        migrations.CreateModel(
            name='ChallengeCreation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('defendant_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challengecreations_against_1', to='core.Account')),
                ('defendant_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='challengecreations_against_2', to='core.Account')),
                ('txn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn')),
            ],
        ),
        migrations.CreateModel(
            name='BalanceUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Event')),
            ],
        ),
        migrations.CreateModel(
            name='ArrowUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrowupdate', models.IntegerField(choices=[(0, 'Neutral'), (1, 'Trust'), (-1, 'Distrust')])),
                ('arrow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Arrow')),
                ('txn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Txn')),
            ],
        ),
        migrations.CreateModel(
            name='ArrowCreation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrow', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Arrow')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Event')),
            ],
        ),
    ]
