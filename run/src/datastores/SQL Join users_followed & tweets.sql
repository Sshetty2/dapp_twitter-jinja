SELECT DISTINCT tweets.pk, tweets.users_pk, tweets.username, tweets.content, tweets.time
FROM tweets
JOIN users_followed
ON users_followed.followed_pk =  tweets.users_pk
WHERE users_followed.users_pk = 2
UNION ALL
SELECT * FROM tweets WHERE users_pk = 2
ORDER BY time DESC;





-- row_place.append(row["pk"]) 
-- row_place.append(row["users_pk"])
-- row_place.append(row["username"])
-- row_place.append(row["content"]) 
-- row_place.append(row["time"]) 